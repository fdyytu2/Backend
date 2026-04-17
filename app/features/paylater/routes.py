from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.core.logging import logger

from app.features.paylater.actions.activation import activate_user_paylater
from app.features.paylater.actions.billing import get_paylater_info

router = APIRouter()

@router.get("/info")
def paylater_info_api(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Cek sisa limit dan jumlah tagihan paylater."""
    logger.info(f"[PAYLATER] 🔍 User {current_user.phone} cek info limit.")
    return get_paylater_info(db, user_id=current_user.id)

@router.post("/activate")
def activate_paylater_api(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Aktivasi akun paylater agar bisa dipakai belanja PPOB."""
    logger.info(f"[PAYLATER] 🚀 Permintaan aktivasi dari User {current_user.phone}")
    return activate_user_paylater(db, user_id=current_user.id)
