from pydantic import BaseModel, Field

class TopupCreateRequest(BaseModel):
    # Minimal 10rb biar gak nyampah di database
    amount: int = Field(..., gt=10000, description="Minimal topup Rp 10.000")
    user_id: str = Field(..., description="ID User yang mau disuntik saldonya")
    note: str = Field("Topup Manual Admin", description="Catatan transaksi")
