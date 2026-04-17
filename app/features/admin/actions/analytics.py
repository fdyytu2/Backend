from sqlalchemy import func
from app.features.users.models import User
from app.features.wallet.models import Wallet
from app.features.ppob.models import PPOBProduct

SYSTEM_ID = "00000000-0000-0000-0000-000000000000"

def get_sys_dashboard_stats(db):
    total_u = db.query(func.count(User.id)).filter(User.is_admin == False).scalar() or 0
    total_bal = db.query(func.sum(Wallet.balance)).scalar() or 0
    sys_bal = db.query(Wallet.balance).filter(Wallet.id == SYSTEM_ID).scalar() or 0
    
    return {
        "users": total_u,
        "liabilities": int(total_bal),
        "vault": int(sys_bal),
        "status": "Healthy" if sys_bal >= 0 else "Nombok"
    }
