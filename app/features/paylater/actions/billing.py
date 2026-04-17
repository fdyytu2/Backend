from fastapi import HTTPException
from app.features.paylater.models import PaylaterAccount
from app.core.logging import logger

def get_paylater_info(db, user_id: str):
    logger.info(f"[PAYLATER-BILL] 🔍 Menarik info billing untuk User ID: {user_id}")
    
    acc = db.query(PaylaterAccount).filter(PaylaterAccount.user_id == user_id).first()
    
    if not acc:
        logger.warning(f"[PAYLATER-BILL] ❓ User {user_id} belum punya akun paylater.")
        return {
            "is_active": False,
            "limit": 0,
            "used_amount": 0,
            "available": 0,
            "message": "Paylater belum diaktifkan"
        }

    available = acc.limit_credit - acc.used_amount
    
    return {
        "is_active": acc.is_active,
        "limit": acc.limit_credit,
        "used_amount": acc.used_amount,
        "available": max(0, available), # Mencegah angka negatif
        "updated_at": acc.updated_at.isoformat() if acc.updated_at else None
    }
