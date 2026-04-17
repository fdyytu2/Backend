from app.core.logging import logger
from datetime import datetime, timedelta
from sqlalchemy import delete
from app.core.db_session import SessionLocal
# Pastikan lu import model yang nampung idempotency key
# Biasanya ada tabel khusus atau numpang di tabel orders (tergantung desain lu)
from app.features.ppob.models import PPOBOrder 



def task_cleanup_idempotency() -> None:
    """
    Menghapus data idempotency yang sudah tua.
    Jalankan tiap malam (00:00) agar database tetap ringan.
    """
    db = SessionLocal()
    try:
        # Tentukan batas umur (misal: hapus yang lebih lama dari 7 hari)
        retention_days = 7
        threshold_date = datetime.now() - timedelta(days=retention_days)

        # Jika lu pake tabel khusus idempotency, hapus di sana.
        # Tapi kalau idempotency nempel di PPOBOrder, kita JANGAN hapus ordernya,
        # cukup kosongkan key-nya atau biarkan saja (tergantung kebutuhan audit).
        
        # Contoh jika lu punya tabel 'IdempotencyKey' khusus:
        # stmt = delete(IdempotencyKey).where(IdempotencyKey.created_at < threshold_date)
        # result = db.execute(stmt)
        
        # Jika idempotency nempel di Order dan lu mau "un-index" biar gak berat:
        # (Biasanya untuk PPOBOrder, kita jarang hapus demi audit trail)
        
        logger.info(f"Cleanup idempotency task started for data older than {threshold_date}")
        
        # Logic cleanup di sini...
        # db.commit()
        
        logger.info("Cleanup idempotency task done.")
        
    except Exception as e:
        logger.error(f"Cleanup idempotency failed: {str(e)}")
        db.rollback()
    finally:
        db.close()
