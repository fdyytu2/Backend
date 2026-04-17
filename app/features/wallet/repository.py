from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.features.wallet.models import LedgerEntry, LedgerJournal, Wallet
from app.core.logging import logger

class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_wallet_by_user_id(self, user_id: str) -> Optional[Wallet]:
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    # 💡 NEW: Fungsi ngebidani dompet baru
    def create_wallet(self, user_id: str) -> Wallet:
        logger.info(f"[WALLET-REPO] 🐣 Creating new wallet for user: {user_id}")
        wallet = Wallet(user_id=user_id)
        self.db.add(wallet)
        return wallet

    def lock_wallet_row(self, wallet_id: str) -> Wallet:
        logger.debug(f"[WALLET-REPO] 🔒 Locking wallet ID: {wallet_id}")
        stmt = (
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if not result:
            logger.error(f"[WALLET-REPO] ❌ Wallet {wallet_id} not found for locking")
            raise ValueError(f"Wallet {wallet_id} not found")
        return result

    def create_journal(self, **kwargs) -> LedgerJournal:
        logger.info(f"[WALLET-REPO] 📝 Creating Journal: {kwargs.get('type')} - {kwargs.get('idempotency_key')}")
        journal = LedgerJournal(**kwargs)
        self.db.add(journal)
        return journal

    def add_entry(self, **kwargs) -> LedgerEntry:
        entry = LedgerEntry(**kwargs)
        self.db.add(entry)
        return entry

    def get_journal_by_idempotency(self, key: str) -> Optional[LedgerJournal]:
        """Cek apakah transaksi sudah pernah diproses sebelumnya."""
        stmt = select(LedgerJournal).where(LedgerJournal.idempotency_key == key)
        return self.db.execute(stmt).scalar_one_or_none()
