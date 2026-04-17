from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.features.users.models import User
from app.features.wallet.models import Wallet
from app.features.ppob.models import PPOBOrder
from app.features.deposit.models import Deposit

def get_admin_dashboard_summary(db: Session):
    # 1. Total User Terdaftar
    total_users = db.query(User).count()
    
    # 2. Total Uang User yang Ngendap di Aplikasi Lu
    total_balance = db.query(func.sum(Wallet.balance)).scalar() or 0
    
    # 3. Transaksi PPOB Hari Ini
    today = date.today()
    today_trx_count = db.query(PPOBOrder).filter(func.date(PPOBOrder.created_at) == today).count()
    
    # 4. Omzet (Uang Masuk dari PPOB) Hari Ini
    today_revenue = db.query(func.sum(PPOBOrder.price_sell)).filter(
        func.date(PPOBOrder.created_at) == today, 
        PPOBOrder.status == "SUCCESS"
    ).scalar() or 0
    
    # 5. Jumlah Topup Manual yang Nunggu Di-ACC
    pending_deposits = db.query(Deposit).filter(
        Deposit.status == "UNPAID", 
        Deposit.payment_method.like("MANUAL%")
    ).count()

    return {
        "total_users": total_users,
        "total_user_balance": total_balance,
        "today_transactions": today_trx_count,
        "today_revenue": today_revenue,
        "pending_manual_deposits": pending_deposits
    }
