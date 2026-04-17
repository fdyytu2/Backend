import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db_base import Base

class TopupStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Topup(Base):
    __tablename__ = "topups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String(50), nullable=False) # Misal: QRIS, BCA_VA
    payment_url = Column(String(255), nullable=True)    # Link ke halaman bayar
    ref_id = Column(String(100), nullable=False, unique=True) # ID dari Payment Gateway
    status = Column(Enum(TopupStatus), default=TopupStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
