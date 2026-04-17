import re
from sqlalchemy.orm import Session
from app.features.ppob.models import PPOBProduct

def extract_nominal(name: str) -> int:
    """Trik sedot nominal dari nama produk (Misal: 'TSEL 10.000' -> 10000, 'ISAT 5K' -> 5000)"""
    clean_name = name.replace('.', '').replace(',', '').upper()

    match_k = re.search(r'\b(\d+)K\b', clean_name)
    if match_k: return int(match_k.group(1)) * 1000

    match_num = re.search(r'\b(\d{4,7})\b', clean_name)
    if match_num: return int(match_num.group(1))

    return 0 

# 💡 NEW: Mesin Penyedot Kuota Data
def extract_quota(name: str) -> str:
    """Sedot angka GB/MB dari nama buat nampilin badge di FE (Misal: 'Data 1.5GB' -> '1.5GB')"""
    match = re.search(r'(\d+(?:\.\d+)?\s*(?:GB|MB))', name, re.IGNORECASE)
    return match.group(1).upper() if match else ""

def get_active_products(db: Session, category: str = None, brand: str = None):
    query = db.query(PPOBProduct).filter(
        PPOBProduct.is_active_provider == True,
        PPOBProduct.is_active_admin == True
    )

    if category:
        query = query.filter(PPOBProduct.category.ilike(f"%{category}%"))
    if brand:
        query = query.filter(PPOBProduct.brand.ilike(f"%{brand}%"))

    products = query.order_by(PPOBProduct.price_sell.asc()).all()

    return [
        {
            "sku": p.sku_code,
            "name": p.name,
            "nominal": extract_nominal(p.name),
            "quota": extract_quota(p.name), # 💡 Tambahan field baru buat FE
            "price": p.price_sell,
            "is_active": True
        } for p in products
    ]
