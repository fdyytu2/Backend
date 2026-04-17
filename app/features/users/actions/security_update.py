from fastapi import HTTPException
from app.core.hashing import verify_password, hash_password, hash_pin, verify_pin
from app.features.users.actions.profile import get_user_profile

def update_user_password(db, user_id: str, old_pass: str, new_pass: str):
    user = get_user_profile(db, user_id)
    if not verify_password(old_pass, user.password_hash):
        raise HTTPException(status_code=400, detail="Password lama salah")
    user.password_hash = hash_password(new_pass)
    db.commit()

def update_user_pin(db, user_id: str, old_pin: str, new_pin: str):
    user = get_user_profile(db, user_id)
    if not user.pin_hash:
        raise HTTPException(status_code=400, detail="PIN belum diset")
    if not verify_pin(old_pin, user.pin_hash):
        raise HTTPException(status_code=400, detail="PIN lama salah")
    user.pin_hash = hash_pin(new_pin)
    db.commit()

# 💡 NEW: Logic Khusus Buat Bikin PIN Pertama Kali
def setup_user_pin(db, user_id: str, new_pin: str):
    user = get_user_profile(db, user_id)
    # Anti-Bypass: Kalau udah punya PIN, tolak!
    if user.pin_hash:
        raise HTTPException(status_code=400, detail="PIN sudah dibuat sebelumnya. Silakan gunakan menu Ubah PIN.")
    
    user.pin_hash = hash_pin(new_pin)
    db.commit()
