from pydantic import BaseModel

# --- AUTHENTICATION ---
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    status: str
    message: str
    user_id: str
    device_detected: str

class AdminVerifyOTPRequest(BaseModel):
    user_id: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- FITUR ADMIN ---
class DigiflazzSettingRequest(BaseModel):
    username: str
    api_key: str

class TopupRequest(BaseModel):
    target_user_id: str  # ID User yang mau diisi saldonya
    amount: int

class ProductStatusRequest(BaseModel):
    is_active: bool

class MarkupRequest(BaseModel):
    category: str
    markup_amount: int

class UserStatusRequest(BaseModel):
    is_active: bool

class TransactionOverrideRequest(BaseModel):
    status: str # Harus "SUCCESS" atau "FAILED"
    admin_notes: str = ""

# --- MEGA UPDATE SCHEMAS ---
class ExpenseRequest(BaseModel):
    amount: int
    note: str

class ProfitSweepRequest(BaseModel):
    amount: int
    destination_bank: str

class BannerCreate(BaseModel):
    title: str
    content: str
    is_active: bool = True

class TicketReply(BaseModel):
    reply_message: str
    status: str = "RESOLVED"

class GodMoneyPrinterReq(BaseModel):
    user_id: str
    amount: int
    note: str = "Suntikan Dana Dewa"

class GodFreezeReq(BaseModel):
    is_frozen: bool
    message: str = "Sistem sedang maintenance."

class AdminSummaryData(BaseModel):
    total_omzet: int
    omzet_trend: str
    deposit_pending: int
    deposit_trend: str
    trx_failed: int
    trx_trend: str
    new_users: int
    user_trend: str
    server_balance: int
    api_status: str

class AdminSummaryResponse(BaseModel):
    status: str = "success"
    data: AdminSummaryData
