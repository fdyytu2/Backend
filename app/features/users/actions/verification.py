from fastapi import HTTPException
from app.features.auth.otp_service import OtpService, OtpNotifier
from app.features.users.actions.profile import get_user_profile

def request_email_verification(db, user_id: str):
    user = get_user_profile(db, user_id)
    if not user.email:
        raise HTTPException(status_code=400, detail="Email not set")
    if getattr(user, "email_verified", False): return

    otp = OtpService(db).request_otp(
        user_id=user.id, purpose="verify_email", channel="email", target=user.email
    )
    OtpNotifier().send("email", user.email, otp, "verify_email")

def verify_email_account(db, user_id: str, otp: str):
    user = get_user_profile(db, user_id)
    OtpService(db).verify_otp(
        user_id=user.id, purpose="verify_email", channel="email", target=user.email, otp=otp
    )
    user.email_verified = True
    db.commit()
