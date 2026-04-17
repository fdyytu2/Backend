from fastapi import HTTPException
from app.core.hashing import hash_pin
from app.features.users.repository import UserRepository

# 🧱 Import Lego Validator
from app.shared.validators import is_valid_pin

# 📹 Import CCTV dari Ruang Mesin
from app.core.logging import logger

def set_user_pin(db, user_id: str, pin: str):
    logger.info(f"[AUTH] 🔒 Memproses permintaan Set/Update PIN untuk User ID: {user_id}")
    
    users = UserRepository(db)
    user = users.get_by_id(user_id)
    
    if not user:
        logger.warning(f"[AUTH] ❌ Gagal Set PIN: User ID {user_id} tidak ditemukan di database.")
        raise HTTPException(status_code=404, detail="User not found")

    pin_norm = pin.strip()
    
    # 🧱 Eksekusi Tukang Razia Format (Lego Validator)
    if not is_valid_pin(pin_norm):
        logger.warning(f"[AUTH] ❌ Gagal Set PIN: Format yang dimasukkan User ID {user_id} salah (Bukan 6 digit murni).")
        raise HTTPException(status_code=400, detail="PIN must be exactly 6 digits of numbers")

    try:
        # Kunci rapat-rapat PIN-nya pakai sistem Hashing sebelum masuk database
        user.pin_hash = hash_pin(pin_norm)
        db.commit()
        logger.info(f"[AUTH] ✅ BERHASIL! PIN untuk User ID {user_id} sukses diperbarui dan dikunci.")
    except Exception as e:
        db.rollback()
        logger.error(f"[AUTH] ❌ TERJADI KESALAHAN SISTEM saat menyimpan PIN User ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while saving PIN")
