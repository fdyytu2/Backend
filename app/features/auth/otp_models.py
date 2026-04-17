import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_base import Base


class UserOTP(Base):
    __tablename__ = "user_otps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # verify_email / verify_phone / reset_pin
    purpose: Mapped[str] = mapped_column(String(50), index=True)

    # email / phone
    channel: Mapped[str] = mapped_column(String(20), index=True)

    # target yang diverifikasi (email/phone normalized)
    target: Mapped[str] = mapped_column(String(255), index=True)

    otp_hash: Mapped[str] = mapped_column(String(255))

    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )