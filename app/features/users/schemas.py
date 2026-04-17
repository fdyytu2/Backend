from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List

# --- PROFILE SCHEMAS ---
class UserMeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    phone: str
    phone_verified: bool = False
    email: str | None = None
    email_verified: bool = False
    account_level: str = "BASIC"
    join_date: str | None = None

class UserUpdateIn(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None

# --- SESSIONS SCHEMAS ---
class SessionItem(BaseModel):
    id: int
    device: str
    last_active: str
    is_current: bool

class SessionListResponse(BaseModel):
    data: List[SessionItem]

# --- SETTINGS SCHEMAS ---
class UserSettingsIn(BaseModel):
    promo_notif: bool
    trx_notif: bool

class UserSettingsResponse(BaseModel):
    status: str
    message: str
    data: UserSettingsIn

# --- SECURITY SCHEMAS ---
class VerifyOtpIn(BaseModel):
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)

class ChangePinIn(BaseModel):
    old_pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

# 💡 NEW: Schema khusus Setup PIN
class SetupPinIn(BaseModel):
    new_pin: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class DeleteAccountIn(BaseModel):
    password: str
