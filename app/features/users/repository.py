# app/features/users/repository.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.features.users.models import User

# Sesuaikan nama fungsi normalisasi di file kamu:
# di tree ada app/shared/phone.py
try:
    from app.shared.phone import normalize_phone  # idealnya mengembalikan "+62..."
except Exception:
    normalize_phone = None  # fallback


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _norm_phone(self, phone: str) -> str:
        phone = (phone or "").strip()
        if not phone:
            return phone
        if normalize_phone:
            try:
                return normalize_phone(phone)
            except Exception:
                # kalau format aneh, fallback ke raw input
                return phone
        return phone

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_phone(self, phone: str) -> User | None:
        phone_n = self._norm_phone(phone)
        stmt = select(User).where(User.phone == phone_n)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, *, phone: str, username: str, password_hash: str) -> User:
        user = User(
            phone=self._norm_phone(phone),
            username=username.strip(),
            password_hash=password_hash,
        )
        self.db.add(user)
        return user