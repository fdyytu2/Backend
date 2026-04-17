# app/features/transfers/repository.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.features.transfers.models import Transfer, TransferStatus


class TransferRepository:
    """
    Repository untuk manajemen data transaksi transfer.
    Menangani query database untuk entitas Transfer.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transfer_id: str) -> Optional[Transfer]:
        return self.db.get(Transfer, transfer_id)

    def get_history_by_user(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Transfer]:
        """
        Ambil riwayat transaksi di mana user adalah PENGIRIM atau PENERIMA.
        Digunakan untuk halaman /transactions di frontend.
        """
        stmt = (
            select(Transfer)
            .where(
                or_(
                    Transfer.sender_user_id == user_id,
                    Transfer.receiver_user_id == user_id
                )
            )
            .order_by(Transfer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_sender_and_idempotency(
        self,
        sender_user_id: str,
        idempotency_key: str,
    ) -> Optional[Transfer]:
        stmt = select(Transfer).where(
            Transfer.sender_user_id == sender_user_id,
            Transfer.idempotency_key == idempotency_key,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Transfer]:
        """Lookup idempotency global (back-compatibility)."""
        stmt = select(Transfer).where(Transfer.idempotency_key == idempotency_key)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        *,
        sender_user_id: str,
        receiver_user_id: str,
        amount: int,
        fee_amount: int = 0,
        status: TransferStatus = TransferStatus.PENDING,
        journal_id: Optional[str] = None,
        idempotency_key: str,
        ref_id: str,
        note: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> Transfer:
        t = Transfer(
            sender_user_id=sender_user_id,
            receiver_user_id=receiver_user_id,
            amount=amount,
            fee_amount=fee_amount,
            status=status,
            journal_id=journal_id,
            idempotency_key=idempotency_key,
            ref_id=ref_id,
            note=note,
            client_ip=client_ip,
        )
        self.db.add(t)
        return t

    def mark_success(self, transfer_id: str, *, journal_id: str) -> Optional[Transfer]:
        t = self.get_by_id(transfer_id)
        if not t:
            return None
        t.status = TransferStatus.SUCCESS
        t.journal_id = journal_id
        from datetime import datetime, timezone
        t.completed_at = datetime.now(timezone.utc)
        return t

    def mark_failed(self, transfer_id: str, *, reason: str) -> Optional[Transfer]:
        t = self.get_by_id(transfer_id)
        if not t:
            return None
        t.status = TransferStatus.FAILED
        t.failed_reason = reason
        return t
