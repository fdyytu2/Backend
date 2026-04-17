import os
import hmac
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.features.deposit.schemas import PaymentMethodsResponse, DepositCheckoutReq, DepositCheckoutRes
from app.features.deposit.actions import invoice, callback

router = APIRouter()

@router.get("/methods", response_model=PaymentMethodsResponse, summary="Ambil Daftar Metode Pembayaran")
def get_payment_methods(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return {
        "data": [
            {
                "category": "Virtual Account",
                "methods": [
                    {"code": "BCAVA", "name": "BCA Virtual Account", "fee_flat": 4000, "fee_percent": 0.0, "icon_url": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Bank_Central_Asia.svg", "description": "Dicek otomatis."},
                    {"code": "BRIVA", "name": "BRI Virtual Account", "fee_flat": 3000, "fee_percent": 0.0, "icon_url": "https://upload.wikimedia.org/wikipedia/commons/9/9e/BRI_2020.svg", "description": "Dicek otomatis."}
                ]
            },
            {
                "category": "E-Wallet & QRIS",
                "methods": [
                    {"code": "QRIS", "name": "QRIS (All Payment)", "fee_flat": 0, "fee_percent": 0.7, "icon_url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Logo_QRIS.svg", "description": "Scan pakai GoPay, OVO, Dana."}
                ]
            }
        ]
    }

@router.post("/checkout", response_model=DepositCheckoutRes, summary="Buat Invoice Topup")
def create_deposit_checkout(payload: DepositCheckoutReq, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        res_data = invoice.create_deposit_invoice(
            db=db, user_id=current_user.id, amount=payload.amount, method=payload.payment_code
        )
        return {"status": "success", "message": "Invoice berhasil dibuat", "data": res_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Gagal membuat invoice deposit.")

# 💡 NEW: Pintu Webhook Resmi Tripay
@router.post("/callback", summary="Webhook Tripay (Jangan Ditembak FE)")
async def tripay_webhook_callback(request: Request, db: Session = Depends(get_db)):
    # 1. Ambil body mentah dan signature dari header
    raw_body = await request.body()
    signature_header = request.headers.get("X-Callback-Signature")
    
    # Ganti dengan Private Key lu dari Dashboard Tripay
    private_key = os.getenv("TRIPAY_PRIVATE_KEY", "your-tripay-private-key").encode()

    # 2. Tameng Keamanan: Hitung HMAC-SHA256
    expected_signature = hmac.new(private_key, raw_body, hashlib.sha256).hexdigest()

    if not signature_header or not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Signature invalid. Hacker detected!")

    # 3. Eksekusi Data
    try:
        data = json.loads(raw_body)
        # Sesuai dokumentasi Tripay
        reference = data.get("reference")
        status = data.get("status")

        # Oper ke mesin pencatat lu
        callback.handle_payment_notification(db, reference=reference, status=status)
        
        # Tripay mewajibkan balasan ini agar mereka berhenti ngirim notif
        return {"success": True}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
