from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.core.logging import logger

# 🧱 Import Lego & Schema
from app.features.topup.schemas import TopupCreateRequest
from app.features.admin.actions.wallet_ops import admin_topup_user

router = APIRouter()

@router.post("/manual-inject")
def manual_topup_api(
    payload: TopupCreateRequest, 
    db: Session = Depends(get_db), 
    admin = Depends(get_current_user)
):
    # Pastikan cuma Admin yang bisa akses jalur ini
    if not admin.is_admin:
        logger.warning(f"[TOPUP-MANUAL] 🚨 User {admin.username} coba-coba suntik saldo!")
        raise HTTPException(status_code=403, detail="Forbidden: Admin Only")

    logger.info(f"[TOPUP-MANUAL] 💸 Admin {admin.username} menyuntik saldo ke User {payload.user_id} sebesar Rp{payload.amount}")
    
    return admin_topup_user(
        db, 
        user_id=payload.user_id, 
        amount=payload.amount, 
        note=payload.note
    )
