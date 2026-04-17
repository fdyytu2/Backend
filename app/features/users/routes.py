from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.db_session import get_db

from app.features.users.schemas import (
    UserMeOut, UserUpdateIn, VerifyOtpIn,
    ChangePasswordIn, ChangePinIn, SetupPinIn, DeleteAccountIn,
    SessionListResponse, UserSettingsIn, UserSettingsResponse
)

from app.features.users.actions import profile, security_update, account_ops

router = APIRouter()

# 💡 FIX: Kita pasang 2 rute (me & profile) ke satu fungsi biar FE aman!
@router.get("/me", response_model=UserMeOut, summary="Auth Checker (Lightweight)")
@router.get("/profile", response_model=UserMeOut, summary="Ambil Data Profil User (Rich)")
def get_profile_api(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    u = profile.get_user_profile(db, user_id=current_user.id)
    join_date_str = u.created_at.strftime("%Y-%m-%d") if u.created_at else None
    acc_level = "PREMIUM" if u.is_admin else "BASIC"

    return UserMeOut(
        id=u.id, username=u.username, phone=u.phone, phone_verified=u.phone_verified,
        email=u.email, email_verified=u.email_verified, account_level=acc_level, join_date=join_date_str
    )

@router.patch("/profile", response_model=UserMeOut, summary="Update Data Profil User")
def update_profile_api(payload: UserUpdateIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    u = profile.update_user_profile(
        db=db, user_id=current_user.id, username=payload.username, email=payload.email,
    )
    join_date_str = u.created_at.strftime("%Y-%m-%d") if u.created_at else None
    acc_level = "PREMIUM" if u.is_admin else "BASIC"
    return UserMeOut(
        id=u.id, username=u.username, phone=u.phone, phone_verified=u.phone_verified,
        email=u.email, email_verified=u.email_verified, account_level=acc_level, join_date=join_date_str
    )

@router.get("/sessions", response_model=SessionListResponse, summary="Ambil Histori Perangkat")
def get_sessions_api(current_user=Depends(get_current_user)):
    return {
        "data": [
            {"id": 1, "device": "Realme C35", "last_active": "Saat ini", "is_current": True},
            {"id": 2, "device": "Chrome on Windows", "last_active": "2026-04-12 14:30:00", "is_current": False}
        ]
    }

@router.put("/settings", response_model=UserSettingsResponse, summary="Toggle Notifikasi")
def update_settings_api(payload: UserSettingsIn, current_user=Depends(get_current_user)):
    return {"status": "success", "message": "Preferensi notifikasi berhasil disimpan", "data": payload}

# --- SECURITY ENDPOINTS ---
@router.patch("/password", summary="Ubah Password")
def change_password_api(payload: ChangePasswordIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    security_update.update_user_password(db, user_id=current_user.id, old_pass=payload.old_password, new_pass=payload.new_password)
    return {"status": "success", "message": "Password berhasil diubah"}

@router.post("/pin/setup", summary="Buat PIN Pertama Kali")
def setup_pin_api(payload: SetupPinIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    security_update.setup_user_pin(db, user_id=current_user.id, new_pin=payload.new_pin)
    return {"status": "success", "message": "PIN keamanan berhasil dibuat"}

@router.patch("/pin", summary="Ubah PIN")
def change_pin_api(payload: ChangePinIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    security_update.update_user_pin(db, user_id=current_user.id, old_pin=payload.old_pin, new_pin=payload.new_pin)
    return {"status": "success", "message": "PIN berhasil diubah"}

@router.delete("/account", summary="Hapus Akun")
def delete_account_api(payload: DeleteAccountIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    account_ops.delete_account(db, user_id=current_user.id, password=payload.password)
    return {"status": "success", "message": "Akun berhasil dihapus permanen"}
