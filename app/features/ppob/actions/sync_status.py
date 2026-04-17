from sqlalchemy.orm import Session
from app.features.ppob.models import PPOBOrder
from app.features.wallet.models import Wallet
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType
from app.features.notifications.actions.notification_service import create_notification
from app.core.logging import logger

SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

def process_order_status(db: Session, ref_id: str, provider_status: str, sn: str = ""):
    order = db.query(PPOBOrder).filter(PPOBOrder.id == ref_id).first()
    
    if not order or order.status != "PENDING":
        return

    w = db.query(Wallet).filter(Wallet.user_id == order.user_id).first()

    if provider_status == "Sukses":
        order.status = "SUCCESS"
        order.sn = sn
        if w:
            w.hold_balance -= order.price_sell
            
        create_notification(db, order.user_id, "✅ Transaksi Berhasil!", f"Isi ulang {order.sku_code} ke {order.customer_no} SUKSES. SN: {sn}", "TRX")
        logger.info(f"[PPOB-SYNC] ✅ Order {ref_id} SUKSES diselesaikan!")

    elif provider_status == "Gagal":
        order.status = "FAILED"
        if w:
            w.hold_balance -= order.price_sell
            
            # 💸 AUTO-REFUND
            post_ledger_entry(
                db, journal_type=JournalType.REFUND, idempotency_key=f"refund-{ref_id}",
                amount=order.price_sell, debit_id=SYSTEM_ACCOUNT_ID, credit_id=w.id,
                debit_type=AccountType.SYSTEM, credit_type=AccountType.USER,
                description=f"Refund PPOB Gagal {ref_id}"
            )
            
        create_notification(db, order.user_id, "❌ Transaksi Gagal", f"Maaf, isi ulang {order.sku_code} ke {order.customer_no} ditolak vendor. Saldo Rp{order.price_sell} otomatis dikembalikan.", "TRX")
        logger.error(f"[PPOB-SYNC] ❌ Order {ref_id} GAGAL. Duit berhasil di-refund!")

    db.commit()
