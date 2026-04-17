from fastapi import HTTPException
from app.features.users.models import User
from app.features.ppob.models import PPOBProduct
from app.features.ppob.utils import detect_operator
from app.core.hashing import verify_pin
from app.core.logging import logger

def validate_purchase_auth(db, user_id: str, pin: str):
    """Mastiin User punya PIN dan PIN-nya bener."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.pin_hash:
        logger.warning(f"[PPOB-VAL] ❌ User {user_id} belum set PIN")
        raise HTTPException(status_code=400, detail="PIN keamanan belum dibuat")
        
    if not verify_pin(pin, user.pin_hash):
        logger.warning(f"[PPOB-VAL] ❌ PIN Salah untuk User {user_id}")
        raise HTTPException(status_code=400, detail="PIN yang Anda masukkan salah")
    return user

def validate_product_and_phone(db, sku_code: str, target_number: str):
    """Mastiin produk ada, aktif, dan nomor HP-nya cocok sama operatornya."""
    # Pastikan query menggunakan sku_code sesuai model
    product = db.query(PPOBProduct).filter(PPOBProduct.sku_code == sku_code).first()
    
    if not product:
        logger.warning(f"[PPOB-VAL] ❌ SKU {sku_code} tidak ditemukan")
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    # Cek status keaktifan (Admin & Provider)
    if not product.is_active_admin or not product.is_active_provider:
        logger.warning(f"[PPOB-VAL] ❌ SKU {sku_code} sedang dinonaktifkan")
        raise HTTPException(status_code=400, detail="Produk sedang tidak tersedia")

    # Validasi Nomor HP vs Brand Operator (Lego Utils)
    if product.category in ["PULSA", "DATA"]:
        detected_brand = detect_operator(target_number)
        if not detected_brand:
            raise HTTPException(status_code=400, detail="Format nomor tujuan salah")
        
        if detected_brand.upper() != product.brand.upper():
            logger.warning(f"[PPOB-VAL] ❌ Mismatch: {target_number} ({detected_brand}) != {product.brand}")
            raise HTTPException(status_code=400, detail=f"Nomor tersebut bukan operator {product.brand}")

    return product
