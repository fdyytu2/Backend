from pydantic import BaseModel, Field

class RepayRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Nominal yang mau dilunasi")
