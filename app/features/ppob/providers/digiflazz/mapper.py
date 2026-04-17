from typing import Any

def map_status(provider_status: str, message: str = "") -> str:
    """
    Nerjemahin status "ajaib" Digiflazz ke status standar aplikasi kita.
    Status Digiflazz biasanya: 'Pending', 'Gagal', 'Sukses'
    """
    status = str(provider_status).upper()
    msg = str(message).upper()

    # 1. Cek Status Sukses
    if status == "SUKSES" or "BERHASIL" in msg:
        return "SUCCESS"

    # 2. Cek Status Gagal
    if status == "GAGAL" or "BATAL" in msg or "REJECT" in msg:
        return "FAILED"

    # 3. Default ke PENDING (paling aman buat saldo user)
    return "PENDING"

def map_product_response(data: dict[str, Any]) -> dict[str, Any]:
    """
    Ngerapiin data pricelist dari Digiflazz biar enak dibaca service.
    """
    return {
        "sku": data.get("buyer_sku_code"),
        "name": data.get("product_name"),
        "category": data.get("category", "").upper(),
        "brand": data.get("brand", "").upper(),
        "type": data.get("type", "").upper(),
        "price_cost": int(data.get("price") or 0),
        "is_active": str(data.get("buyer_product_status")).lower() in ("true", "1", "lancar"),
        "desc": data.get("desc", "")
    }

def map_transaction_response(data: dict[str, Any]) -> dict[str, Any]:
    """
    Ngerapiin data hasil tembak pulsa / cek status.
    """
    status_raw = data.get("status", "PENDING")
    message = data.get("message", "")
    
    return {
        "ref_id": data.get("ref_id"),
        "status": map_status(status_raw, message),
        "message": message,
        "sn": data.get("sn"), # Serial Number / Token PLN
        "price_final": int(data.get("price") or 0), # Harga modal asli pas kejadian
        "telepon": data.get("customer_no")
    }
