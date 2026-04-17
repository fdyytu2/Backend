from fastapi import HTTPException
from app.features.paylater.models import PaylaterAccount
from app.core.logging import logger

def activate_user_paylater(db, user_id: str):
    logger.info(f"[PAYLATER-ACT] 🚀 Memproses aktivasi untuk User ID: {user_id}")
    
    # 1. Cek apakah user sudah punya akun paylater
    existing = db.query(PaylaterAccount).filter(PaylaterAccount.user_id == user_id).first()
    if existing:
        if existing.is_active:
            return {"status": "active", "message": "Paylater Anda sudah aktif!"}
        else:
            existing.is_active = True
            db.commit()
            logger.info(f"[PAYLATER-ACT] ✅ Akun {user_id} diaktifkan kembali.")
            return {"status": "active", "message": "Paylater berhasil diaktifkan kembali!"}

    # 2. Buat akun baru dengan limit default (Rp20.000)
    try:
        new_acc = PaylaterAccount(
            user_id=user_id,
            limit_credit=20000,
            used_amount=0,
            is_active=True
        )
        db.add(new_acc)
        db.commit()
        logger.info(f"[PAYLATER-ACT] ✨ Akun Paylater baru tercipta untuk {user_id} dengan limit Rp20.000")
        return {"status": "success", "message": "Selamat! Paylater Anda sudah aktif dengan limit Rp20.000"}
    except Exception as e:
        db.rollback()
        logger.error(f"[PAYLATER-ACT] ❌ Gagal aktivasi User {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengaktifkan Paylater")
