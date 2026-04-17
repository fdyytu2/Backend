from app.core.db_session import SessionLocal
from app.features.ppob.repository import PPOBRepository
from app.features.ppob.providers.digiflazz.client import DigiflazzClient
from app.features.ppob.actions.sync_status import process_order_status
from app.core.config import settings
from app.core.logging import logger

def task_poll_pending():
    db = SessionLocal()
    try:
        repo = PPOBRepository(db)
        pending_orders = repo.list_pending_orders(limit=50)

        if not pending_orders:
            return

        logger.info(f"[JOB-POLL] 🔍 Mengecek {len(pending_orders)} transaksi gantung...")
        client = DigiflazzClient(username=settings.digiflazz_user, key=settings.digiflazz_key)

        for order in pending_orders:
            payload = {
                "username": settings.digiflazz_user,
                "buyer_last_id": order.id 
            }
            res = client.hit_transaction(payload)

            if res.get("success"):
                data = res.get("data", {})
                status_provider = data.get("status") 
                sn = data.get("sn", "")

                if status_provider in ["Sukses", "Gagal"]:
                    # 💡 Panggil mesin sentral buat urus Auto-Refund & Notif
                    process_order_status(db, ref_id=order.id, provider_status=status_provider, sn=sn)

    except Exception as e:
        logger.error(f"[JOB-POLL] ❌ Gagal polling: {e}")
        db.rollback()
    finally:
        db.close()
