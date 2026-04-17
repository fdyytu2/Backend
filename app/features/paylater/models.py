from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db_base import Base
from app.shared.generators import generate_transaction_id

class PaylaterAccount(Base):
    __tablename__ = "paylater_accounts"

    # 🧱 Pakai Lego Generator: PAY-20260409-XXXX
    id = Column(String(36), primary_key=True, default=lambda: generate_transaction_id("PAY"))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    
    limit_credit = Column(Integer, default=20000) # Limit awal Rp20.000
    used_amount = Column(Integer, default=0)      # Jumlah hutang yang terpakai
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
