from app.core.logging import logger
from app.features.deposit.models import Deposit
from app.features.wallet.actions.setup import ensure_user_wallet
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType

# 💡 NEW: Import mesin notifikasi
from app.features.notifications.actions.notification_service import create_notification

SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

def handle_payment_notification(db, reference: str, status: str):
    deposit = db.query(Deposit).filter(Deposit.reference == reference).first()

    if not deposit:
        logger.warning(f"[DEPOSIT-CALLBACK] ❓ Referensi {reference} tidak ditemukan")
        return {"status": "error", "message": "Not found"}

    if deposit.status == "PAID":
        logger.info(f"[DEPOSIT-CALLBACK] ⏭️ Referensi {reference} sudah berstatus PAID. Diabaikan.")
        return {"status": "ignored", "message": "Already processed"}

    if status == "PAID":
        logger.info(f"[DEPOSIT-CALLBACK] 💰 PEMBAYARAN DITERIMA! Invoice: {deposit.id}, Amount: Rp{deposit.amount}")

        deposit.status = "PAID"
        wallet_id = ensure_user_wallet(db, deposit.user_id)

        try:
            post_ledger_entry(
                db,
                journal_type=JournalType.TOPUP,
                idempotency_key=f"topup-{deposit.id}",
                amount=deposit.amount,
                debit_id=SYSTEM_ACCOUNT_ID,
                debit_type=AccountType.SYSTEM,
                credit_id=wallet_id,
                credit_type=AccountType.USER,
                description=f"Deposit via {deposit.payment_method} ({deposit.id})"
            )
            
            # 💡 NEW: Tembak Notifikasi ke User!
            create_notification(
                db, 
                user_id=deposit.user_id, 
                title="💸 Saldo Mendarat!", 
                message=f"Topup Rp{deposit.amount} via {deposit.payment_method} udah masuk brankas lu, Bosku. Gas checkout!", 
                notif_type="TRX"
            )
            
            db.commit()
            logger.info(f"[DEPOSIT-CALLBACK] ✅ SALDO BERHASIL MASUK ke User {deposit.user_id}")
            return {"status": "success"}
            
        except Exception as e:
            db.rollback()
            logger.error(f"[DEPOSIT-CALLBACK] ❌ GAGAL SUNTIK SALDO untuk {deposit.id}: {e}")
            return {"status": "error", "message": "Failed to update ledger"}

    # Kalau status dari Tripay selain PAID (misal FAILED/EXPIRED)
    deposit.status = status
    db.commit()
    return {"status": "ignored", "message": f"Status updated to {status}"}
