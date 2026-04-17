import json
import os
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db_session import get_db
from app.core.tokens import decode_access_token
from app.core.logging import logger
from app.features.users.models import User

# Actions & Policies
from app.features.admin.policies import check_super_admin_policy
from app.features.admin.actions.wallet_ops import admin_topup_user, god_print_money
from app.features.admin.actions.auth import admin_login_step_1, admin_login_step_2
from app.features.admin.actions.summary import get_admin_dashboard_summary
from app.features.admin.actions.settings import get_digiflazz_config, set_setting

# Providers
from app.features.ppob.providers.digiflazz.client import DigiflazzClient
from app.features.ppob.providers.digiflazz.parser import DigiflazzParser

# Schemas
from app.features.admin.schemas import (
    AdminLoginRequest, AdminLoginResponse, AdminVerifyOTPRequest, 
    TokenResponse, GodMoneyPrinterReq, GodFreezeReq,
    AdminSummaryResponse, DigiflazzSettingRequest
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/login/step-2")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id: raise HTTPException(status_code=401, detail="Invalid Token")
    except: raise HTTPException(status_code=401, detail="Token Expired/Corrupt")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden: Admin Only")
    return user

# --- ENDPOINTS ---

@router.post("/login/step-1", response_model=AdminLoginResponse)
def login_step_1(payload: AdminLoginRequest, request: Request, db: Session = Depends(get_db)):
    user_agent = request.headers.get("user-agent", "Unknown Device")
    result = admin_login_step_1(db, payload.username, payload.password, user_agent)
    return {"status": "success", "message": "OTP Sent", "user_id": result["user_id"], "device_detected": result["device"]}

@router.post("/login/step-2", response_model=TokenResponse)
def login_step_2(payload: AdminVerifyOTPRequest, db: Session = Depends(get_db)):
    token = admin_login_step_2(db, payload.user_id, payload.otp)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/summary", response_model=AdminSummaryResponse)
def admin_summary_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    stats = get_admin_dashboard_summary(db)
    return {"status": "success", "data": stats}

@router.get("/vendor/digiflazz")
def get_vendor_settings(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    return {"status": "success", "data": get_digiflazz_config(db)}

@router.post("/vendor/digiflazz/update")
def update_vendor_settings(payload: DigiflazzSettingRequest, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    set_setting(db, "DIGIFLAZZ_USERNAME", payload.username, "Username")
    set_setting(db, "DIGIFLAZZ_API_KEY", payload.api_key, "API Key")
    return {"status": "success", "message": "Settings Updated!"}

@router.post("/vendor/digiflazz/test")
def test_vendor_connection(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    cfg = get_digiflazz_config(db)
    
    # Alur 1 File 1 Tugas: Client -> Parser
    client = DigiflazzClient(username=cfg["username"], key=cfg["api_key"], base_url=cfg["base_url"])
    raw_res = client.get_balance()
    result = DigiflazzParser.parse_balance_response(raw_res)
    
    if result["status"] == "success":
        return {"status": "success", "message": "Koneksi Normal", "balance": result["balance"]}
    
    return {"status": "error", "message": "Gagal Cek Saldo", "detail": result["message"]}

@router.post("/god/print-money")
def god_money(payload: GodMoneyPrinterReq, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    return god_print_money(db, payload.user_id, payload.amount, payload.note)

@router.post("/god/maintenance")
def toggle_maintenance(payload: GodFreezeReq, admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    file = "maintenance_mode.json"
    if payload.is_frozen:
        with open(file, "w") as f: json.dump({"is_frozen": True, "message": payload.message}, f)
        return {"message": "ZA WARUDO! System Frozen."}
    else:
        if os.path.exists(file): os.remove(file)
        return {"message": "Time flows зgain."}



# --- ENDPOINTS FRONTEND: PRODUCT & MARGIN ---
from typing import Dict
from pydantic import BaseModel
from app.features.admin.actions.ppob_ops import (
    sync_digiflazz_products, get_margins, set_margins, get_all_products, toggle_product_status
)

class MarginSaveReq(BaseModel):
    # Pakai tipe dict biar bisa nerima object {"type": "fixed", "value": 500}
    margins: Dict[str, dict]

class ToggleReq(BaseModel):
    sku: str
    isActive: bool

@router.post("/products/sync")
def endpoint_sync_products(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    cfg = get_digiflazz_config(db)
    return sync_digiflazz_products(db, cfg)

@router.get("/products/margin")
def endpoint_get_margins(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    return {"status": "success", "data": get_margins(db)}

@router.post("/products/margin")
def endpoint_save_margins(payload: MarginSaveReq, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    set_margins(db, payload.margins)
    return {"status": "success", "message": "Margin berhasil disimpan"}

@router.get("/products")
def endpoint_get_products(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    products = get_all_products(db)

    data_fe = []
    for p in products:
        data_fe.append({
            "sku": p.sku_code,
            "name": p.name,
            "brand": p.brand,
            "category": p.category, # 💡 NEW: Frontend sekarang bisa akses field kategori
            "type": p.type,
            "originalPrice": p.price_base,
            "isActive": p.is_active_admin
        })
    return {"status": "success", "data": data_fe}

@router.post("/products/toggle")
def endpoint_toggle_product(payload: ToggleReq, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    success = toggle_product_status(db, payload.sku, payload.isActive)
    if success:
        return {"status": "success", "message": f"Status produk {payload.sku} berhasil diubah"}
    return {"status": "error", "message": "SKU tidak ditemukan"}

# --- ENDPOINTS FRONTEND: TRANSACTIONS ---
from typing import Optional
from app.features.admin.actions.ppob_ops import (
    get_paginated_orders, sync_order_status_provider, override_order_status, get_order_raw_logs
)

class ManualUpdateReq(BaseModel):
    status: str # Wajib isi "SUCCESS" atau "FAILED"
    notes: str = "Manual Update by Admin"

@router.get("/transactions")
def get_admin_transactions(
    offset: int = 0, limit: int = 20, status: Optional[str] = None, customer_no: Optional[str] = None,
    db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    check_super_admin_policy(admin)
    total, items = get_paginated_orders(db, offset, limit, status, customer_no)
    
    # Mapping Format sesuai standar Frontend
    data_fe = []
    for o in items:
        data_fe.append({
            "id": o.id,
            "userId": o.user_id,
            "sku": o.sku_code,
            "customerNo": o.customer_no,
            "priceSell": o.price_sell,
            "status": o.status,
            "sn": o.sn,
            "createdAt": o.created_at.isoformat(),
            "updatedAt": o.updated_at.isoformat()
        })
        
    return {"status": "success", "total": total, "limit": limit, "offset": offset, "data": data_fe}

@router.post("/transactions/{order_id}/sync-status")
def endpoint_sync_trx(order_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    cfg = get_digiflazz_config(db)
    result = sync_order_status_provider(db, order_id, cfg)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/transactions/{order_id}/manual-update")
def endpoint_manual_update_trx(order_id: str, payload: ManualUpdateReq, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    try:
        # Panggil fungsi lo yang udah ada logic refund/ledger-nya
        override_order_status(db, order_id, payload.status.upper(), payload.notes)
        return {"status": "success", "message": f"Order {order_id} berhasil di-set ke {payload.status.upper()}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{order_id}/logs")
def endpoint_get_trx_logs(order_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    cfg = get_digiflazz_config(db)
    raw = get_order_raw_logs(db, order_id, cfg)
    return {"status": "success", "data": raw}

# --- ENDPOINTS FRONTEND: DEPOSIT & PAYMENT METHOD ---
from typing import Optional, List, Dict, Any
from app.features.admin.actions.finance import get_admin_deposits, process_manual_deposit, get_payment_configs, update_payment_configs

class PaymentConfigReq(BaseModel):
    manualBanks: Optional[List[Dict[str, Any]]] = None
    tripay: Optional[Dict[str, str]] = None

@router.get("/payments")
def endpoint_get_payments(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    return {"status": "success", "data": get_payment_configs(db)}

@router.post("/payments")
def endpoint_update_payments(payload: PaymentConfigReq, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    update_payment_configs(db, payload.model_dump(exclude_unset=True))
    return {"status": "success", "message": "Konfigurasi Payment berhasil disimpan!"}

@router.get("/deposits")
def endpoint_get_deposits(status: Optional[str] = None, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    deposits = get_admin_deposits(db, status)
    
    data_fe = []
    for d in deposits:
        data_fe.append({
            "id": d.id,
            "userId": d.user_id,
            "amount": d.amount,
            "method": d.payment_method,
            "reference": d.reference,
            "status": d.status,
            "createdAt": d.created_at.isoformat() if d.created_at else None
        })
    return {"status": "success", "data": data_fe}

@router.post("/deposits/{deposit_id}/approve")
def endpoint_approve_deposit(deposit_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    success, msg = process_manual_deposit(db, deposit_id, "APPROVE")
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@router.post("/deposits/{deposit_id}/reject")
def endpoint_reject_deposit(deposit_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    success, msg = process_manual_deposit(db, deposit_id, "REJECT")
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

# --- ENDPOINTS FRONTEND: USER MANAGEMENT ---
from app.features.admin.actions.user_ops import (
    get_admin_user_list, toggle_user_status, manual_balance_adjustment
)

class UserStatusResponse(BaseModel):
    id: str
    status: str

class AddBalanceReq(BaseModel):
    amount: int
    note: str = "Adjustment by Admin"

@router.get("/users")
def endpoint_get_users(search: Optional[str] = None, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    users = get_admin_user_list(db, search)
    
    data_fe = []
    for u in users:
        data_fe.append({
            "id": u.id,
            "name": u.username,
            "phone": u.phone,
            "balance": u.wallet.balance if u.wallet else 0,
            "status": "active" if u.is_active else "blocked",
            "createdAt": u.created_at.isoformat()
        })
    return {"status": "success", "data": data_fe}

@router.post("/users/{user_id}/status")
def endpoint_toggle_user(user_id: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    user = toggle_user_status(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    new_status = "active" if user.is_active else "blocked"
    return {"status": "success", "message": f"User status is now {new_status}", "data": {"status": new_status}}

@router.post("/users/{user_id}/balance")
def endpoint_manual_balance(user_id: str, payload: AddBalanceReq, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    check_super_admin_policy(admin)
    success, msg = manual_balance_adjustment(db, user_id, payload.amount, payload.note)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}
