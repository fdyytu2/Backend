from sqlalchemy.orm import Session
from app.features.notifications.models import Notification

def create_notification(db: Session, user_id: str, title: str, message: str, notif_type: str = "INFO"):
    notif = Notification(user_id=user_id, title=title, message=message, type=notif_type)
    db.add(notif)
    db.commit()

def get_user_notifications(db: Session, user_id: str):
    notifs = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(50).all()
    unread_count = db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).count()

    data = []
    for n in notifs:
        data.append({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        })
    return {"data": data, "unread_count": unread_count}

def mark_all_as_read(db: Session, user_id: str):
    db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
    db.commit()

# 💡 NEW: Fungsi Buat Buka Detail + Auto Read
def get_notification_detail(db: Session, notif_id: str, user_id: str):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user_id).first()
    
    if not notif:
        return None
        
    # Kalau belum dibaca, otomatis ganti statusnya jadi True pas dibuka
    if not notif.is_read:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
        
    return {
        "id": notif.id,
        "title": notif.title,
        "message": notif.message,
        "type": notif.type,
        "is_read": notif.is_read,
        "created_at": notif.created_at.isoformat()
    }
