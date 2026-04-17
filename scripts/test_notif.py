import sys
import os

# Biar Python ngebaca folder app lu dari root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db_session import SessionLocal
from app.features.users.models import User
from app.features.notifications.actions.notification_service import create_notification

db = SessionLocal()

try:
    # Cari tumbal (User pertama yang ada di database lu)
    user = db.query(User).first()

    if user:
        print(f"🔔 Mengirim notifikasi ke user: {user.phone}...")
        
        # Tembak Notif Promo
        create_notification(
            db, user_id=user.id, 
            title="🎉 Promo Dadakan!", 
            message="Bosku, ada diskon pulsa all operator khusus buat lu hari ini. Gas checkout!", 
            notif_type="PROMO"
        )
        
        # Tembak Notif Transaksi
        create_notification(
            db, user_id=user.id, 
            title="💸 Saldo Masuk", 
            message="Topup Rp50.000 udah mendarat cantik di brankas lu.", 
            notif_type="TRX"
        )
        
        print("✅ BUM! Notifikasi berhasil ditembak ke database.")
    else:
        print("❌ Waduh, database lu masih kosong, belum ada user satupun.")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
