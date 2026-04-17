from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.db_session import get_db
from app.api.v1.deps import get_current_user

# 🧱 Import Atomic Actions Wallet
from app.features.wallet.actions.history import get_user_transaction_history
from app.features.wallet.actions.balance import get_wallet_summary, get_user_balance
from app.features.wallet.actions.setup import ensure_user_wallet

router = APIRouter()

@router.get("/summary", response_model=Dict[str, Any])
def read_wallet_summary(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Ambil ringkasan saldo, hold balance, dan status wallet."""
    return get_wallet_summary(db, user_id=current_user.id)

@router.get("/balance")
def read_balance(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Cukup ambil angka saldo aktif saja."""
    balance = get_user_balance(db, user_id=current_user.id)
    return {"balance": balance, "currency": "IDR"}

@router.post("/ensure")
def initialize_wallet(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Inisialisasi wallet jika belum ada (biasanya dipanggil saat login pertama)."""
    wallet_id = ensure_user_wallet(db, user_id=current_user.id)
    return {"status": "ok", "wallet_id": wallet_id}

@router.get("/history")
def wallet_history_api(limit: int = 20, offset: int = 0, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Lihat buku tabungan (riwayat mutasi)."""
    return get_user_transaction_history(db, user_id=current_user.id, limit=limit, offset=offset)
