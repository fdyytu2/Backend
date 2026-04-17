from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.db_base import Base
from app.shared.generators import generate_transaction_id

class Deposit(Base):
    __tablename__ = "deposits"

    # Pakai prefix DEP agar jelas ini transaksi Deposit
    id = Column(String(36), primary_key=True, default=lambda: generate_transaction_id("DEP"))
    user_id = Column(String(36), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String(50))
    reference = Column(String(100), unique=True, index=True) # ID dari Tripay
    status = Column(String(20), default="UNPAID") # UNPAID, PAID, FAILED
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
