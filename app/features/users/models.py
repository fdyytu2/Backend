import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_base import Base

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)

    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    password_hash: Mapped[str] = mapped_column(String(255))
    pin_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now_utc, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now_utc, onupdate=_now_utc)

    # ==========================================
    # RELATIONSHIPS
    # ==========================================

    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    transfers_sent: Mapped[List["Transfer"]] = relationship("Transfer", foreign_keys="Transfer.sender_user_id", back_populates="sender")
    
    transfers_received: Mapped[List["Transfer"]] = relationship("Transfer", foreign_keys="Transfer.receiver_user_id", back_populates="receiver")
    
    orders: Mapped[List["PPOBOrder"]] = relationship("PPOBOrder", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(username={self.username}, phone={self.phone})>"

# 🧱 IMPORT NYATA DI BAWAH SINI BIAR SQLALCHEMY NGGAK BINGUNG
# Taruh di paling bawah buat mencegah Circular Import
from app.features.wallet.models import Wallet
from app.features.transfers.models import Transfer
from app.features.ppob.models import PPOBOrder
