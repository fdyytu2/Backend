from app.features.wallet.repository import WalletRepository
from app.core.logging import logger

def get_user_balance(db, user_id: str) -> int:
    repo = WalletRepository(db)
    wallet = repo.get_wallet_by_user_id(user_id)
    balance = wallet.balance if wallet else 0
    logger.info(f"[BALANCE] 🔍 Cek saldo User {user_id}: Rp{balance}")
    return balance

def get_wallet_summary(db, user_id: str):
    repo = WalletRepository(db)
    wallet = repo.get_wallet_by_user_id(user_id)
    if not wallet:
        return {"balance": 0, "available_balance": 0, "hold_balance": 0}
    
    hold = getattr(wallet, 'hold_balance', 0)
    summary = {
        "wallet_id": str(wallet.id),
        "balance": wallet.balance,
        "available_balance": wallet.balance - hold,
        "hold_balance": hold,
        "currency": "IDR"
    }
    logger.info(f"[BALANCE] 📊 Summary User {user_id}: Net Rp{summary['available_balance']} (Hold: Rp{hold})")
    return summary
