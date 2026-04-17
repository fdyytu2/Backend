from sqlalchemy.orm import Session
from sqlalchemy import select
from app.features.ppob.models import PPOBProduct, PPOBOrder
from app.core.logging import logger

class PPOBRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, *, category: str | None = None) -> list[PPOBProduct]:
        stmt = select(PPOBProduct).where(
            PPOBProduct.is_active_admin == True,
            PPOBProduct.is_active_provider == True
        )
        if category:
            stmt = stmt.where(PPOBProduct.category == category.upper())
        return list(self.db.execute(stmt.order_by(PPOBProduct.price_sell.asc())).scalars().all())

    def upsert_product(self, **data) -> PPOBProduct:
        p = self.db.execute(select(PPOBProduct).where(PPOBProduct.sku_code == data['sku_code'])).scalar_one_or_none()
        
        if p:
            # Update harga modal dan status provider
            p.price_base = data['price_base']
            p.price_sell = data['price_sell'] # Hasil hitungan markup rule
            p.is_active_provider = data['is_active_provider']
            logger.info(f"[PPOB-REPO] 🔄 Updated SKU: {data['sku_code']}")
            return p

        logger.info(f"[PPOB-REPO] ✨ New Product Auto-Init: {data['sku_code']}")
        p = PPOBProduct(**data)
        self.db.add(p)
        return p
