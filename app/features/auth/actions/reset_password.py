from fastapi import HTTPException
from app.core.hashing import hash_password
from app.features.users.repository import UserRepository
from app.features.auth.otp_service import OtpService
from app.shared.phone import normalize_id_phone

def reset_user_password(db, phone: str, otp: str, new_password: str, channel: str):
    users = UserRepository(db)
    user = users.get_by_phone(normalize_id_phone(phone))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    OtpService(db).verify_otp(
        user_id=user.id, purpose="reset_password",
        channel=channel, target=user.phone, otp=otp
    )

    user.password_hash = hash_password(new_password)
    db.commit()
