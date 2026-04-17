from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.hashing import verify_password
from app.core.tokens import create_access_token
from app.features.users.repository import UserRepository
from app.shared.phone import normalize_id_phone

# 📹 Import CCTV dari Ruang Mesin
from app.core.logging import logger

def login_user(db, phone: str, password: str):
    phone_norm = normalize_id_phone(phone)
    logger.info(f"[AUTH] 🔑 Seseorang mencoba login dengan nomor: {phone_norm}")

    users = UserRepository(db)
    now = datetime.now(timezone.utc)
    user = users.get_by_phone(phone_norm)

    # 1. Filter Pertama: Cek ketersediaan User
    if not user:
        logger.warning(f"[AUTH] ❌ Login ditolak: Nomor {phone_norm} tidak terdaftar di database.")
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    # 2. Filter Kedua (Keamanan): Cek apakah akun sedang digembok
    if user.locked_until and now < user.locked_until:
        logger.warning(f"[AUTH] 🔒 Serangan tertahan! Ada yang mencoba login ke akun {phone_norm} yang sedang digembok.")
        raise HTTPException(status_code=429, detail="Account locked temporarily. Please try again later.")

    # 3. Filter Ketiga: Cocokkan Password
    if not verify_password(password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        logger.warning(f"[AUTH] ❌ Password salah untuk {phone_norm}. Percobaan gagal: {user.failed_login_attempts}/{settings.login_max_attempts}")
        
        # Kalau gagalnya kelewatan batas, gembok akunnya!
        if user.failed_login_attempts >= settings.login_max_attempts:
            user.locked_until = now + timedelta(minutes=settings.login_lock_minutes)
            logger.error(f"[AUTH] 🚨 BRUTE-FORCE DETECTED! Mengunci akun {phone_norm} selama {settings.login_lock_minutes} menit.")
        
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    # 4. Lolos Semua Filter: Berikan Kunci Akses (Token)
    logger.info(f"[AUTH] ✅ Akses diberikan untuk {phone_norm} (User ID: {user.id})")
    
    # Bersihkan catatan hitam gagal login karena sekarang sudah berhasil
    user.failed_login_attempts = 0
    user.locked_until = None 
    user.last_login_at = now
    
    db.commit()
    return create_access_token(subject=user.id)
