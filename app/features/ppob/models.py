from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_base import Base
from app.shared.generators import generate_transaction_id

if TYPE_CHECKING:
    from app.features.users.models import User

class PPOBProduct(Base):
    __tablename__ = "ppob_products"
    
    # ID Produk internal
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_transaction_id("PRD"))
    provider: Mapped[str] = mapped_column(String(20), default="DIGIFLAZZ", index=True)
    sku_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(30), index=True)
    brand: Mapped[str] = mapped_column(String(30), index=True)
    type: Mapped[str] = mapped_column(String(30), index=True)
    price_base: Mapped[int] = mapped_column(Integer, default=0)
    price_sell: Mapped[int] = mapped_column(Integer, default=0)
    is_active_provider: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active_admin: Mapped[bool] = mapped_column(Boolean, default=True)
    is_promo: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class PPOBOrder(Base):
    __tablename__ = "ppob_orders"

    # 🧱 Gunakan Resi Cantik: PPOB-20260409-XXXX
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_transaction_id("PPOB"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    sku_code: Mapped[str] = mapped_column(String(80), index=True)
    customer_no: Mapped[str] = mapped_column(String(80), index=True)
    price_sell: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), index=True, default="PENDING")
    provider_ref_id: Mapped[str] = mapped_column(String(80), index=True, nullable=True)
    sn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="orders")
