from sqlalchemy.exc import IntegrityError
from app.features.wallet.repository import WalletRepository
from app.core.logging import logger

def ensure_user_wallet(db, user_id: str) -> str:
    repo = WalletRepository(db)
    wallet = repo.get_wallet_by_user_id(user_id)
    if not wallet:
        try:
            with db.begin_nested():
                wallet = repo.create_wallet(user_id)
                db.flush()
                logger.info(f"[WALLET-SETUP] ✨ Dompet baru tercipta untuk User: {user_id}")
        except IntegrityError:
            db.rollback()
            wallet = repo.get_wallet_by_user_id(user_id)
    return wallet.id
