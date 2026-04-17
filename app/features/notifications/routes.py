from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.features.notifications.schemas import NotificationListOut, NotificationItem
from app.features.notifications.actions import notification_service

router = APIRouter()

@router.get("/", response_model=NotificationListOut, summary="Ambil Lonceng Notifikasi User")
def endpoint_get_notifications(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return notification_service.get_user_notifications(db, user_id=current_user.id)

@router.patch("/read-all", summary="Tandai Semua Dibaca")
def endpoint_read_all_notifications(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    notification_service.mark_all_as_read(db, user_id=current_user.id)
    return {"status": "success", "message": "Semua notifikasi ditandai sudah dibaca"}

# 💡 NEW: Endpoint Buat Buka Detail Lonceng
@router.get("/{notif_id}", response_model=NotificationItem, summary="Lihat Detail Notifikasi")
def endpoint_get_notif_detail(notif_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    notif = notification_service.get_notification_detail(db, notif_id=notif_id, user_id=current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notifikasi tidak ditemukan atau bukan milik Anda")
    return notif
