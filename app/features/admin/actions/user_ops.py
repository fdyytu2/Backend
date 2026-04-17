import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.features.users.models import User
from app.features.wallet.models import Wallet
from app.features.wallet.actions.setup import ensure_user_wallet
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType
from app.core.logging import logger

SYSTEM_ID = "00000000-0000-0000-0000-000000000000"

def get_admin_user_list(db: Session, search: str = None):
    # Join ke wallet biar dapet saldo langsung
    query = db.query(User).join(Wallet)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_filter),
                User.phone.contains(search)
            )
        )
    
    return query.all()

def toggle_user_status(db: Session, user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Flip status is_active
    user.is_active = not user.is_active
    db.commit()
    
    status_label = "Active" if user.is_active else "Blocked"
    logger.info(f"[ADMIN] User {user.username} status changed to {status_label}")
    return user

def manual_balance_adjustment(db: Session, user_id: str, amount: int, note: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, "User tidak ditemukan"
    
    w_id = ensure_user_wallet(db, user.id)
    
    # Logic: Kalau amount positif = Tambah, Kalau negatif = Kurangi
    desc = f"[MANUAL ADJ] {note}"
    
    try:
        post_ledger_entry(
            db, 
            journal_type=JournalType.TOPUP, 
            idempotency_key=f"manual-{uuid.uuid4()}",
            amount=abs(amount), 
            # Jika amount positif: Debit System, Credit User (User nambah)
            # Jika amount negatif: Debit User, Credit System (User berkurang)
            debit_id=SYSTEM_ID if amount > 0 else w_id,
            debit_type=AccountType.SYSTEM if amount > 0 else AccountType.USER,
            credit_id=w_id if amount > 0 else SYSTEM_ID,
            credit_type=AccountType.USER if amount > 0 else AccountType.SYSTEM,
            description=desc
        )
        db.commit()
        return True, "Saldo berhasil disesuaikan"
    except Exception as e:
        db.rollback()
        logger.error(f"Gagal manual adjust: {e}")
        return False, str(e)
