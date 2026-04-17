from pydantic import BaseModel, Field
from typing import List, Optional

class PaymentMethodItem(BaseModel):
    code: str
    name: str
    fee_flat: int
    fee_percent: float
    icon_url: str
    description: Optional[str] = None

class PaymentCategory(BaseModel):
    category: str
    methods: List[PaymentMethodItem]

class PaymentMethodsResponse(BaseModel):
    data: List[PaymentCategory]

# 💡 NEW: Bungkusan Buat Checkout
class DepositCheckoutReq(BaseModel):
    amount: int = Field(..., ge=10000, description="Minimal topup 10rb")
    payment_code: str = Field(..., description="Kode metode bayar dari API GET methods")

class DepositCheckoutData(BaseModel):
    deposit_id: str
    reference: str
    amount: int
    checkout_url: str

class DepositCheckoutRes(BaseModel):
    status: str
    message: str
    data: DepositCheckoutData
