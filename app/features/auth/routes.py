from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.features.users.repository import UserRepository
from app.features.auth.schemas import RegisterRequest, LoginRequest, TokenResponse, SetPinRequest, OTPReq, ResetPassReq
from app.features.auth.actions import login, register, manage_pin, reset_password
from app.features.auth.otp_service import OtpService

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    token = register.register_user(db=db, phone=payload.phone, username=payload.username, password=payload.password)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login.login_user(db=db, phone=payload.phone, password=payload.password)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/set-pin")
def set_pin(payload: SetPinRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    manage_pin.set_user_pin(db=db, user_id=current_user.id, pin=payload.pin)
    return {"status": "success", "message": "PIN berhasil diamankan"}

@router.post("/otp/request")
def request_otp(payload: OTPReq, db: Session = Depends(get_db)):
    users = UserRepository(db)
    user = users.get_by_phone(payload.phone)
    if not user:
        raise HTTPException(status_code=404, detail="Nomor HP tidak terdaftar")

    otp_service = OtpService(db)
    # 🐛 FIX: Gunakan user.phone (dari DB) sebagai target, bukan payload.phone
    otp_code = otp_service.request_otp(
        user_id=user.id,
        purpose=payload.purpose,
        channel=payload.channel,
        target=user.phone 
    )
    return {"status": "success", "message": f"Kode OTP telah dibuat (Cek Terminal Termux)"}

@router.post("/reset-password")
def reset_password_route(payload: ResetPassReq, db: Session = Depends(get_db)):
    reset_password.reset_user_password(
        db=db, 
        phone=payload.phone, 
        otp=payload.otp, 
        new_password=payload.new_password, 
        channel=payload.channel
    )
    return {"status": "success", "message": "Password berhasil direset, silakan login ulang"}
