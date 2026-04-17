import json
from fastapi import HTTPException
from app.core.hashing import verify_password
from app.core.tokens import create_access_token
from app.features.auth.otp_service import OtpService, OtpNotifier
from app.features.users.models import User
from app.core.logging import logger

def admin_login_step_1(db, username, password, user_agent):
    logger.info(f"[ADMIN-AUTH] 🔑 Percobaan login Admin: {username}")
    user = db.query(User).filter(User.username == username, User.is_admin == True).first()

    if not user or not verify_password(password, user.password_hash):
        logger.warning(f"[ADMIN-AUTH] ❌ Login Admin gagal: {username} (Password Salah)")
        raise HTTPException(status_code=401, detail="Kredensial tidak valid")

    target_email = user.email or "admin@ppob.com"
    otp_code = OtpService(db).request_otp(
        user_id=user.id, purpose="admin_login", channel="email",
        target=target_email
    )
    OtpNotifier().send("email", target_email, otp_code, "admin_login")
    return {"user_id": user.id, "device": user_agent}

def admin_login_step_2(db, user_id, otp):
    logger.info(f"[ADMIN-AUTH] 🔐 Memverifikasi OTP Admin ID: {user_id}")
    
    # 🐛 FIX: Cari user dulu biar dapet email aslinya dari DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Admin tidak ditemukan")
        
    target_email = user.email or "admin@ppob.com"
    OtpService(db).verify_otp(user_id, "admin_login", "email", target_email, otp)
    
    return create_access_token(subject=user_id)
