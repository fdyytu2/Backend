import json
from fastapi import HTTPException
from app.features.ppob.models import PPOBProduct, PPOBOrder
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.actions.holding import release_user_hold
from app.features.wallet.enums import JournalType, AccountType
from app.core.logging import logger
from app.shared.generators import generate_transaction_id
from app.features.admin.actions.settings import get_setting, set_setting
from app.features.ppob.providers.digiflazz.client import DigiflazzClient
from app.shared.pagination import apply_pagination

SYSTEM_ID = "00000000-0000-0000-0000-000000000000"

# --- FUNGSI LAMA ---
def mass_markup(db, category, amount):
    category_up = category.upper()
    logger.info(f"[ADMIN-PPOB] 📈 Markup massal kategori {category_up}: +Rp{amount}")
    prods = db.query(PPOBProduct).filter(PPOBProduct.category == category_up).all()
    for p in prods:
        p.price_sell += amount
    db.commit()

def override_order_status(db, order_id, new_status, notes):
    order = db.query(PPOBOrder).filter(PPOBOrder.id == order_id).first()
    if not order or order.status != "PENDING":
        raise HTTPException(status_code=400, detail="Order tidak ditemukan atau status bukan PENDING")
    
    if new_status == "FAILED":
        release_user_hold(db, order.user_id, order.price_sell)
        order.status = "FAILED"
    elif new_status == "SUCCESS":
        post_ledger_entry(
            db, journal_type=JournalType.PAYMENT, idempotency_key=generate_transaction_id("OVR"),
            amount=order.price_sell, debit_id=order.user_id, credit_id=SYSTEM_ID,
            credit_type=AccountType.SYSTEM, description=f"Override Success: {notes}"
        )
        order.status = "SUCCESS"
    db.commit()

# --- MESIN KALKULATOR HARGA (BARU!) ---
def recalculate_all_prices(db):
    """Ngitung ulang Harga Jual (price_sell) berdasarkan Harga Modal (price_base) + Margin"""
    margins = get_margins(db)
    products = db.query(PPOBProduct).all()
    
    for p in products:
        # Cari margin berdasarkan brand, kalau gak ada kasih default 0
        m_config = margins.get(p.brand, {"type": "fixed", "value": 0})
        m_type = m_config.get("type", "fixed")
        m_val = float(m_config.get("value", 0))

        if m_type == "percent":
            markup = p.price_base * (m_val / 100)
            p.price_sell = int(p.price_base + markup)
        else:
            p.price_sell = int(p.price_base + m_val)
            
    db.commit()
    logger.info("[ADMIN-PPOB] 🧮 Selesai update Harga Jual (price_sell) ke semua produk.")

# --- FUNGSI FRONTEND ---
def get_margins(db) -> dict:
    margins_str = get_setting(db, "DYNAMIC_MARGINS", "{}")
    try: return json.loads(margins_str)
    except: return {}

def set_margins(db, margins: dict):
    set_setting(db, "DYNAMIC_MARGINS", json.dumps(margins), "Dynamic Margins by Brand")
    # 💡 SETIAP ADMIN GANTI MARGIN, HARGA JUAL OTOMATIS BERUBAH!
    recalculate_all_prices(db) 
    return True

def sync_digiflazz_products(db, config: dict):
    client = DigiflazzClient(username=config["username"], key=config["api_key"], base_url=config["base_url"])
    res = client.get_pricelist()

    if not res.get("success"): return {"status": "error", "message": f"Vendor Error: {res.get('error')}"}

    digiflazz_data = res.get("data", {}).get("data", [])
    if isinstance(digiflazz_data, dict): return {"status": "error", "message": "Format vendor tidak dikenali"}
    if not digiflazz_data or not isinstance(digiflazz_data, list): return {"status": "error", "message": "Data kosong"}

    sync_count = 0
    unique_brands = set()

    for item in digiflazz_data:
        sku = item.get("buyer_sku_code")
        brand = item.get("brand")
        if brand: unique_brands.add(brand)

        product = db.query(PPOBProduct).filter(PPOBProduct.sku_code == sku).first()
        vendor_status = str(item.get("seller_product_status")).lower() in ["normal", "1", "true"]

        if product:
            product.price_base = item.get("price", 0)
            product.is_active_provider = vendor_status
            product.name = item.get("product_name", product.name)
            product.category = item.get("category", product.category)
        else:
            new_prod = PPOBProduct(
                sku_code=sku, name=item.get("product_name"), category=item.get("category"),
                brand=brand, type=item.get("type"), price_base=item.get("price", 0),
                is_active_provider=vendor_status, is_active_admin=True
            )
            db.add(new_prod)
        sync_count += 1

    try:
        db.commit()

        # Format Margin Baru
        current_margins = get_margins(db)
        margin_updated = False
        for b in unique_brands:
            if b not in current_margins:
                current_margins[b] = {"type": "fixed", "value": 0}
                margin_updated = True
            elif isinstance(current_margins[b], (int, float, str)):
                try: old_val = float(current_margins[b])
                except: old_val = 0
                current_margins[b] = {"type": "fixed", "value": old_val}
                margin_updated = True

        if margin_updated: set_margins(db, current_margins)

        # 💡 SETIAP SELESAI SYNC, OTOMATIS HITUNG HARGA JUAL!
        recalculate_all_prices(db)

        return {"status": "success", "message": f"Berhasil sinkronisasi {sync_count} produk!"}
    except Exception as e:
        db.rollback()
        logger.error(f"[SYNC ERROR] {e}")
        return {"status": "error", "message": "Database error saat nyimpan produk"}

def get_all_products(db): return db.query(PPOBProduct).all()

def toggle_product_status(db, sku: str, is_active: bool):
    product = db.query(PPOBProduct).filter(PPOBProduct.sku_code == sku).first()
    if not product: return False
    product.is_active_admin = is_active
    db.commit()
    return True

# --- TRANSACTION LOGIC ---
def get_paginated_orders(db, offset: int = 0, limit: int = 20, status: str = None, customer_no: str = None):
    query = db.query(PPOBOrder).order_by(PPOBOrder.created_at.desc())
    if status: query = query.filter(PPOBOrder.status == status.upper())
    if customer_no: query = query.filter(PPOBOrder.customer_no.contains(customer_no))
    return apply_pagination(query, offset, limit)

def sync_order_status_provider(db, order_id: str, config: dict):
    # Logika Sync Order (Sama kayak sebelumnya)
    order = db.query(PPOBOrder).filter(PPOBOrder.id == order_id).first()
    if not order: return {"status": "error", "message": "Order tidak ditemukan"}

    client = DigiflazzClient(username=config["username"], key=config["api_key"], base_url=config["base_url"])
    ref_id = order.provider_ref_id or order.idempotency_key

    from app.features.ppob.providers.digiflazz.parser import DigiflazzParser
    raw_res = client.check_transaction(order.sku_code, order.customer_no, ref_id)
    parsed = DigiflazzParser.parse_transaction_response(raw_res)

    if parsed["status"] == "error": return parsed

    new_status = parsed["mapped_status"]
    if order.status == "PENDING" and new_status != "PENDING":
        override_order_status(db, order.id, new_status, f"Auto-Sync: {parsed['message']}")
    
    if parsed["sn"]: order.sn = parsed["sn"]
    db.commit()
    return {"status": "success", "data": parsed}

def get_order_raw_logs(db, order_id: str, config: dict):
    order = db.query(PPOBOrder).filter(PPOBOrder.id == order_id).first()
    if not order: return {"status": "error", "message": "Order tidak ditemukan"}
    client = DigiflazzClient(username=config["username"], key=config["api_key"], base_url=config["base_url"])
    ref_id = order.provider_ref_id or order.idempotency_key
    return client.check_transaction(order.sku_code, order.customer_no, ref_id)
