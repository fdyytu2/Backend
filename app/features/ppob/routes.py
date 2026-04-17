from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
import json

from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.features.wallet.actions.balance import get_user_balance
from app.features.wallet.actions.setup import ensure_user_wallet
from app.features.ppob.actions.validation import validate_purchase_auth, validate_product_and_phone
from app.features.ppob.actions.pricing import calculate_hybrid_split
from app.features.ppob.actions.checkout import process_checkout
from app.features.ppob.actions.product_service import get_active_products
from app.features.ppob.models import PPOBOrder
from app.features.ppob.schemas import ProductListFEResponse, CheckoutReq, InvoiceDetailOut, TransactionHistoryListOut
from app.features.ppob.actions.sync_status import process_order_status
from app.features.admin.actions.settings import get_digiflazz_config
from app.features.ppob.providers.digiflazz.client import DigiflazzClient
from pydantic import BaseModel

router = APIRouter()

@router.get("/products", response_model=ProductListFEResponse)
def endpoint_get_products(category: Optional[str] = Query(None), brand: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return {"data": get_active_products(db, category, brand)}

@router.post("/transactions/checkout")
def endpoint_checkout_ppob(payload: CheckoutReq, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    validate_purchase_auth(db, user_id=current_user.id, pin=payload.pin)
    product = validate_product_and_phone(db, sku_code=payload.sku_code, target_number=payload.target_number)
    wallet_id = ensure_user_wallet(db, user_id=current_user.id)
    balance = get_user_balance(db, user_id=current_user.id)

    total_price, shortfall, from_saldo = calculate_hybrid_split(product.price_sell, balance, payload.use_paylater)
    if shortfall > 0 and not payload.use_paylater:
        raise HTTPException(status_code=400, detail="Saldo lu kurang, Bos!")

    order = process_checkout(db, current_user.id, product, from_saldo, shortfall, wallet_id, payload.target_number)
    return {"status": "success", "message": "Transaksi diproses", "order_id": order.id, "order_status": order.status}

@router.get("/transactions", response_model=TransactionHistoryListOut)
def endpoint_get_all_transactions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    orders = db.query(PPOBOrder).filter(PPOBOrder.user_id == current_user.id).order_by(PPOBOrder.created_at.desc()).all()
    data = [{"order_id": o.id, "sku_code": o.sku_code, "target_number": o.customer_no, "price": o.price_sell, "status": o.status, "sn": o.sn, "date": o.created_at.isoformat()} for o in orders]
    return {"data": data}

@router.get("/transactions/{order_id}", response_model=InvoiceDetailOut)
def endpoint_get_order_status(order_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    order = db.query(PPOBOrder).filter(PPOBOrder.id == order_id, PPOBOrder.user_id == current_user.id).first()
    if not order: raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return InvoiceDetailOut(order_id=order.id, sku_code=order.sku_code, target_number=order.customer_no, price=order.price_sell, status=order.status, sn=order.sn, date=order.created_at.isoformat())

@router.post("/webhook")
async def digiflazz_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = json.loads(await request.body())
        data = payload.get("data", {})
        ref_id, status, sn = data.get("ref_id"), data.get("status"), data.get("sn", "")
        if ref_id and status in ["Sukses", "Gagal"]: process_order_status(db, ref_id=ref_id, provider_status=status, sn=sn)
        return {"status": "success"}
    except Exception as e: return {"status": "ignored", "error": str(e)}

class PLNInquiryReq(BaseModel):
    customer_no: str

@router.post("/inquiry/pln", summary="Cek Nama Pelanggan Token PLN")
def endpoint_inquiry_pln(payload: PLNInquiryReq, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cfg = get_digiflazz_config(db)
    client = DigiflazzClient(username=cfg["username"], key=cfg["api_key"], base_url=cfg["base_url"])
    res = client.inquiry_pln(payload.customer_no)
    
    if res.get("success"):
        # Unwrap data (karena digiflazz masukinnya ke data.data)
        raw_data = res.get("data", {})
        core_data = raw_data.get("data", raw_data)
        
        # 💡 CEK STATUS GAGAL DARI DIGIFLAZZ
        if core_data.get("status") == "Gagal":
            err_msg = core_data.get("message", "Gagal cek meteran.")
            raise HTTPException(status_code=400, detail=err_msg)
            
        customer_name = "Nama Tidak Ditemukan"
        
        if "desc" in core_data and isinstance(core_data["desc"], dict):
            nama = core_data["desc"].get("nama")
            tarif = core_data["desc"].get("tarif", "")
            daya = core_data["desc"].get("daya", "")
            if nama: customer_name = f"{nama} / {tarif} / {daya}VA"
        elif "customer_name" in core_data and core_data["customer_name"]:
            customer_name = core_data["customer_name"]
        elif "sn" in core_data and core_data["sn"]:
            customer_name = core_data["sn"]
            
        return {
            "status": "success",
            "customer_no": payload.customer_no,
            "name": customer_name
        }
        
    raise HTTPException(status_code=400, detail="Koneksi ke server PLN terputus.")
