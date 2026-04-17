from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.hashing import hash_password
from app.core.tokens import create_access_token
from app.features.users.repository import UserRepository
from app.features.wallet.actions.setup import ensure_user_wallet

# 🧱 Import Lego dari Kotak Perkakas
from app.shared.phone import normalize_id_phone
from app.shared.validators import is_strong_password

# 📹 Import CCTV dari Ruang Mesin
from app.core.logging import logger

def register_user(db, phone: str, username: str, password: str):
    logger.info(f"[AUTH] 🚀 Mencoba register user baru dengan nomor HP: {phone}")
    
    users = UserRepository(db)
    phone_norm = normalize_id_phone(phone)
    username_norm = username.strip()                   
    
    if not username_norm:
        logger.warning(f"[AUTH] ❌ Register gagal ({phone_norm}): Username kosong")
        raise HTTPException(status_code=400, detail="Username is required")

    # 🧱 Eksekusi Razia Password!
    if not is_strong_password(password):
        logger.warning(f"[AUTH] ❌ Register gagal ({phone_norm}): Password terlalu lemah")
        raise HTTPException(
            status_code=400, 
            detail="Password minimal 8 karakter, wajib ada huruf besar dan angka."
        )

    try:
        user = users.create(
            phone=phone_norm,
            username=username_norm,
            password_hash=hash_password(password),
        )
        db.flush() # Simpan sementara buat dapet ID
        
        # 🐛 Bug Fixed: Panggil fungsi yang bener sesuai import
        logger.info(f"[AUTH] 💼 Membuatkan brankas dompet untuk {phone_norm}...")
        ensure_user_wallet(db, user.id)
        
        db.commit() # Patenkan ke database!
        db.refresh(user)
        
        logger.info(f"[AUTH] ✅ MANTAP! User {username_norm} berhasil terdaftar dengan ID: {user.id}")
        return create_access_token(subject=user.id)
        
    except (IntegrityError, SQLAlchemyError) as e:
        db.rollback()
        logger.error(f"[AUTH] ❌ Gagal simpan ke DB untuk {phone_norm}: Nomor/Username sudah ada.")
        raise HTTPException(status_code=400, detail="Phone/username already used")
