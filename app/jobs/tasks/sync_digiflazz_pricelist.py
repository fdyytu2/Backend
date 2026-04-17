from app.core.db_session import SessionLocal
from app.features.ppob.repository import PPOBRepository
from app.features.ppob.providers.digiflazz.client import DigiflazzClient
from app.core.config import settings
from app.core.logging import logger

def task_sync_pricelist():
    logger.info("[JOB-SYNC] 🔄 Memulai sinkronisasi harga Digiflazz...")
    db = SessionLocal()
    try:
        # 1. Panggil Kurir Digiflazz
        client = DigiflazzClient(username=settings.digiflazz_user, key=settings.digiflazz_key)
        payload = {"cmd": "prepaid", "username": settings.digiflazz_user} # Sesuai doc Digiflazz
        
        response = client.hit_transaction(payload) # Pakai client yang udah ada Circuit Breaker
        
        if not response.get("success"):
            logger.error(f"[JOB-SYNC] ❌ Gagal ambil harga: {response.get('error')}")
            return

        products_data = response.get("data", [])
        repo = PPOBRepository(db)
        
        # 2. Update massal ke Database
        for item in products_data:
            # Kalkulasi harga jual (Bisa ditambah logic markup rule di sini)
            modal = item.get("price")
            jual = modal + 500 # Contoh: Untung flat Rp500
            
            repo.upsert_product(
                sku_code=item.get("buyer_sku_code"),
                name=item.get("product_name"),
                category=item.get("category"),
                brand=item.get("brand"),
                type=item.get("type"),
                price_base=modal,
                price_sell=jual,
                is_active_provider=item.get("seller_product_status") == True,
                provider="DIGIFLAZZ"
            )
        
        db.commit()
        logger.info(f"[JOB-SYNC] ✅ Berhasil sinkronisasi {len(products_data)} produk.")
        
    except Exception as e:
        logger.error(f"[JOB-SYNC] ❌ Terjadi kesalahan: {e}")
        db.rollback()
    finally:
        db.close()
