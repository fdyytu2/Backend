from app.features.wallet.repository import WalletRepository
from app.features.wallet.actions.setup import ensure_user_wallet
from app.core.logging import logger

def hold_user_funds(db, user_id: str, amount: int):
    if amount <= 0: raise ValueError("Amount must be positive")
    repo = WalletRepository(db)
    wallet_id = ensure_user_wallet(db, user_id)
    wallet = repo.lock_wallet_row(wallet_id)
    
    hold = getattr(wallet, 'hold_balance', 0)
    if (wallet.balance - hold) < amount:
        logger.warning(f"[WALLET-HOLD] ❌ Saldo tidak cukup untuk HOLD: User {user_id}, Butuh: Rp{amount}")
        raise ValueError("Insufficient available balance")
    
    wallet.hold_balance = hold + amount
    db.flush()
    logger.info(f"[WALLET-HOLD] ❄️ Berhasil membekukan dana Rp{amount} untuk User {user_id}")
    return True

def release_user_hold(db, user_id: str, amount: int):
    repo = WalletRepository(db)
    wallet_id = ensure_user_wallet(db, user_id)
    wallet = repo.lock_wallet_row(wallet_id)
    
    hold = getattr(wallet, 'hold_balance', 0)
    if hold < amount:
        logger.error(f"[WALLET-HOLD] ❌ Gagal RELEASE: Hold balance tidak cukup. User {user_id}")
        raise ValueError("Hold balance insufficient")
        
    wallet.hold_balance = hold - amount
    db.flush()
    logger.info(f"[WALLET-HOLD] 🔥 Berhasil mencairkan (release) dana Rp{amount} untuk User {user_id}")
    return True
