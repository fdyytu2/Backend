import uuid
from app.features.users.models import User
from app.features.wallet.actions.setup import ensure_user_wallet
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType

SYSTEM_ID = "00000000-0000-0000-0000-000000000000"

def admin_topup_user(db, username, amount):
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        return {"status": "error", "message": "User tidak ditemukan"}
        
    w_id = ensure_user_wallet(db, user.id)
    
    # 🐛 FIX: Samain Enum dengan standar lu (SYSTEM & USER)
    post_ledger_entry(
        db, journal_type=JournalType.TOPUP, idempotency_key=f"adm-{uuid.uuid4()}",
        amount=amount, debit_id=SYSTEM_ID, debit_type=AccountType.SYSTEM,
        credit_id=w_id, credit_type=AccountType.USER,
        description=f"Manual Topup to @{username}"
    )
    db.commit()
    return {"status": "success", "amount": amount, "message": f"Berhasil isi {amount} ke {username}"}

def god_print_money(db, target_id, amount, note):
    w_id = ensure_user_wallet(db, target_id)
    post_ledger_entry(
        db, journal_type=JournalType.TOPUP, idempotency_key=f"god-{uuid.uuid4()}",
        amount=amount, debit_id=SYSTEM_ID, debit_type=AccountType.SYSTEM,
        credit_id=w_id, credit_type=AccountType.USER, description=f"[GOD] {note}"
    )
    db.commit()
    
    # 🐛 FIX: Tambahin balasan kembalian (Return)
    return {
        "status": "success", 
        "message": f"ZA WARUDO! Rp{amount} berhasil dicetak dari udara kosong ke dompet user.",
        "amount": amount
    }
