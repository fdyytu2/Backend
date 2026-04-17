from fastapi import HTTPException
from app.features.ppob.models import PPOBOrder
from app.features.paylater.models import PaylaterAccount
from app.features.wallet.models import Wallet
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType

# 🧱 Provider & Config Digiflazz
from app.features.admin.actions.settings import get_digiflazz_config
from app.features.ppob.providers.digiflazz.client import DigiflazzClient
from app.features.ppob.providers.digiflazz.parser import DigiflazzParser

from app.shared.generators import generate_transaction_id
from app.core.logging import logger

SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

def process_checkout(db, user_id: str, product, amount_saldo, shortfall, wallet_id, target_number: str):
    order_id = generate_transaction_id(prefix="PPOB")
    logger.info(f"[PPOB] 🛒 Memulai checkout {order_id} untuk {product.sku_code} ke {target_number}")

    # 1. Handle Paylater (Jika hybrid)
    paylater_acc = None
    if shortfall > 0:
        paylater_acc = db.query(PaylaterAccount).filter(PaylaterAccount.user_id == user_id).first()
        if not paylater_acc or not paylater_acc.is_active:
            raise HTTPException(status_code=400, detail="Paylater tidak aktif")
        if shortfall > (paylater_acc.limit_credit - paylater_acc.used_amount):
            raise HTTPException(status_code=400, detail="Limit Paylater tidak cukup")
        paylater_acc.used_amount += shortfall

    # 2. Potong Saldo Utama (HOLD DULU)
    w = None
    if amount_saldo > 0:
        post_ledger_entry(
            db, journal_type=JournalType.PAYMENT,
            idempotency_key=f"hold-{order_id}",
            amount=amount_saldo, debit_id=wallet_id,
            credit_id=SYSTEM_ACCOUNT_ID, credit_type=AccountType.SYSTEM
        )
        w = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        w.hold_balance += amount_saldo

    # 3. Create Order Record (Status Awal PENDING)
    new_order = PPOBOrder(
        id=order_id,
        user_id=user_id,
        sku_code=product.sku_code,
        customer_no=target_number,
        price_sell=product.price_sell + (2500 if shortfall > 0 else 0),
        status="PENDING",
        idempotency_key=order_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 4. TEMBAK DIGIFLAZZ REAL-TIME! 🚀
    try:
        cfg = get_digiflazz_config(db)
        client = DigiflazzClient(username=cfg["username"], key=cfg["api_key"], base_url=cfg.get("base_url", "https://api.digiflazz.com/v1"))
        
        # Ini bakal bertindak sebagai eksekusi "BELI" karena order_id kita baru!
        logger.info(f"[PPOB] 📡 Mengirim Order {order_id} ke Vendor...")
        raw_res = client.check_transaction(sku=new_order.sku_code, customer_no=new_order.customer_no, ref_id=new_order.id)
        parsed = DigiflazzParser.parse_transaction_response(raw_res)

        if parsed["status"] == "success":
            new_status = parsed["mapped_status"] # Isinya: SUCCESS, FAILED, PENDING
            new_order.status = new_status
            if parsed.get("sn"):
                new_order.sn = parsed["sn"]

            # 🛑 LOGIC GAGAL: Langsung Balikin Duit (Refund) Otomatis!
            if new_status == "FAILED":
                logger.error(f"[PPOB] ❌ Vendor menolak transaksi {order_id}: {parsed.get('message')}. Auto-refund jalan...")
                if amount_saldo > 0 and w:
                    w.hold_balance -= amount_saldo # Lepas hold
                    # Catat jurnal pengembalian duit dari Brankas ke User
                    post_ledger_entry(
                        db, journal_type=JournalType.REFUND,
                        idempotency_key=f"refund-{order_id}",
                        amount=amount_saldo, debit_id=SYSTEM_ACCOUNT_ID, credit_id=wallet_id,
                        debit_type=AccountType.SYSTEM, credit_type=AccountType.USER,
                        description=f"Refund PPOB Gagal {order_id}"
                    )
                if shortfall > 0 and paylater_acc:
                    paylater_acc.used_amount -= shortfall # Balikin limit paylater
            
            # ✅ LOGIC SUKSES: Lepas status tahanan saldo
            elif new_status == "SUCCESS":
                logger.info(f"[PPOB] ✅ Transaksi {order_id} SUKSES! SN: {new_order.sn}")
                if amount_saldo > 0 and w:
                    w.hold_balance -= amount_saldo
            
            # ⏳ LOGIC PENDING: Biarin saldo tetep ditahan. Mesin Worker lu yang bakal nerusin.
            elif new_status == "PENDING":
                logger.info(f"[PPOB] ⏳ Transaksi {order_id} masih PENDING di Vendor.")

        db.commit()
    except Exception as e:
        logger.error(f"[PPOB] ⚠️ Gagal komunikasi sama API Digiflazz untuk {order_id}: {e}")
        db.rollback() # Biarin aja status DB tetap PENDING, nanti disapu sama Worker lu

    return new_order
