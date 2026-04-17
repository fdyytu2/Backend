from sqlalchemy.orm import Session
from app.features.deposit.models import Deposit
from app.features.wallet.actions.setup import ensure_user_wallet
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType
from app.features.notifications.actions.notification_service import create_notification
from app.core.logging import logger

SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

def get_admin_deposits(db: Session, status: str = None):
    query = db.query(Deposit)
    if status:
        query = query.filter(Deposit.status == status)
    return query.order_by(Deposit.created_at.desc()).all()

def process_manual_deposit(db: Session, deposit_id: str, action: str):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    
    if not deposit:
        return False, "Deposit tidak ditemukan di database"
    if deposit.status != "UNPAID":
        return False, f"Deposit sudah diproses sebelumnya (Status saat ini: {deposit.status})"

    if action == "APPROVE":
        deposit.status = "PAID"
        wallet_id = ensure_user_wallet(db, deposit.user_id)
        
        try:
            # 💸 Suntik saldo dengan double-entry system
            post_ledger_entry(
                db, journal_type=JournalType.TOPUP, idempotency_key=f"manual-topup-{deposit.id}",
                amount=deposit.amount, debit_id=SYSTEM_ACCOUNT_ID, credit_id=wallet_id,
                debit_type=AccountType.SYSTEM, credit_type=AccountType.USER,
                description=f"Manual Deposit Approved ({deposit.id})"
            )
            
            # 🔔 Kasih tau user kalau saldo udah masuk
            create_notification(db, deposit.user_id, "💰 Deposit Disetujui!", f"Topup manual Rp{deposit.amount} berhasil diproses Admin. Gas transaksi!", "TRX")
            db.commit()
            return True, "Deposit di-approve! Saldo user berhasil ditambah."
            
        except Exception as e:
            db.rollback()
            logger.error(f"[ADMIN-FINANCE] Gagal ledger manual deposit {deposit.id}: {e}")
            return False, "Sistem gagal menyuntikkan saldo ke Wallet"
            
    elif action == "REJECT":
        deposit.status = "FAILED"
        create_notification(db, deposit.user_id, "❌ Deposit Ditolak", f"Topup Rp{deposit.amount} ditolak Admin. Pastikan bukti transfer yang lu kirim valid ya.", "INFO")
        db.commit()
        return True, "Deposit berhasil ditolak."

    return False, "Perintah (action) tidak dikenali."

def get_payment_configs(db: Session):
    # Dummy config untuk frontend
    return {
        "manualBanks": [{"code": "MANUAL_BCA", "name": "BCA 12345678 a/n Bos Besar"}],
        "tripay": {"active": True}
    }

def update_payment_configs(db: Session, data: dict):
    pass
