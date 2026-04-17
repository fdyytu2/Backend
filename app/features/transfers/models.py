# app/features/transfers/models.py
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db_base import Base

# Antisipasi Circular Import untuk Type Hinting
if TYPE_CHECKING:
    from app.features.users.models import User
    from app.features.wallet.models import LedgerJournal


class TransferStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
        CheckConstraint("fee_amount >= 0", name="ck_transfers_fee_non_negative"),
        UniqueConstraint("sender_user_id", "idempotency_key", name="uq_transfers_sender_idempotency"),
        
        Index("ix_transfers_status_created_at", "status", "created_at"),
        Index("ix_transfers_sender_created_at", "sender_user_id", "created_at"),
        Index("ix_transfers_receiver_created_at", "receiver_user_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # USER REFERENCES
    sender_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    receiver_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    # AMOUNTS
    amount: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    fee_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # LEDGER LINK
    journal_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("ledger_journals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # BUSINESS/AUDIT
    ref_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    status: Mapped[TransferStatus] = mapped_column(
        SAEnum(TransferStatus, name="transfer_status"),
        default=TransferStatus.PENDING,
        index=True,
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(120),
        index=True,
        nullable=False,
    )

    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    client_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # TIMESTAMPS
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # ==========================================
    # RELATIONSHIPS (Solusi untuk KeyError: 'sender')
    # ==========================================
    
    # Hubungkan kembali ke model User sesuai back_populates di User model
    sender: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[sender_user_id], 
        back_populates="transfers_sent"
    )
    
    receiver: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[receiver_user_id], 
        back_populates="transfers_received"
    )

    # Relationship ke Journal (Opsional tapi disarankan)
    journal: Mapped[Optional["LedgerJournal"]] = relationship("LedgerJournal")

    def __repr__(self) -> str:
        return f"<Transfer(id={self.id}, amount={self.amount}, status={self.status})>"
