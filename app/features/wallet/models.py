from datetime import datetime, timezone
from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, Index, text
from sqlalchemy.orm import relationship
from app.core.db_base import Base
from app.shared.generators import generate_transaction_id # 🧱 Pake Lego kita

def get_utc_now():
    return datetime.now(timezone.utc)

class Wallet(Base):
    __tablename__ = "wallets"
    # ID Dompet: WLT-20260409-XXXX
    id = Column(String(36), primary_key=True, default=lambda: generate_transaction_id("WLT"))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    balance = Column(BigInteger, default=0, nullable=False, server_default=text("0"))
    hold_balance = Column(BigInteger, default=0, nullable=False, server_default=text("0"))
    currency = Column(String(3), default="IDR", server_default=text("'IDR'"))
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="wallet")

class LedgerJournal(Base):
    __tablename__ = "ledger_journals"
    # ID Jurnal: JRN-20260409-XXXX
    id = Column(String(36), primary_key=True, default=lambda: generate_transaction_id("JRN"))
    type = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    idempotency_key = Column(String(100), unique=True, nullable=False, index=True)
    reference_id = Column(String(50), nullable=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    entries = relationship("LedgerEntry", back_populates="journal", cascade="all, delete-orphan")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(String(36), primary_key=True, default=lambda: generate_transaction_id("ENT"))
    journal_id = Column(String(36), ForeignKey("ledger_journals.id", ondelete="CASCADE"), nullable=False)
    account_type = Column(String(20), nullable=False)
    account_id = Column(String(36), nullable=False, index=True)
    direction = Column(String(10), nullable=False)
    amount = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    journal = relationship("LedgerJournal", back_populates="entries")

Index("ix_ledger_entries_query", LedgerEntry.account_id, LedgerEntry.created_at)
