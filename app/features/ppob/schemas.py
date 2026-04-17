from pydantic import BaseModel, Field
from typing import List, Optional

# --- CONTRACT FRONTEND (PRODUCTS) ---
class ProductFEItem(BaseModel):
    sku: str = Field(..., description="KODE WAJIB: ID unik produk")
    name: str = Field(..., description="Nama produk buat ditampilin")
    nominal: int = Field(..., description="Angka nominal biar gampang disortir")
    price: int = Field(..., description="HARGA JUAL FINAL (Modal + Margin)")
    is_active: bool = Field(..., description="Flag kalau produk lagi gangguan/kosong")

class ProductListFEResponse(BaseModel):
    data: List[ProductFEItem]

# --- REQUEST SCHEMAS ---
class CheckoutReq(BaseModel):
    sku_code: str
    target_number: str
    pin: str
    use_paylater: bool = False

class HybridOrderRequest(BaseModel):
    product_code: str
    target_number: str
    use_paylater: bool = False
    pin: str = Field(min_length=6, max_length=6)

# 💡 NEW: INVOICE & HISTORY SCHEMAS
class InvoiceDetailOut(BaseModel):
    order_id: str
    sku_code: str
    target_number: str
    price: int
    status: str
    sn: str | None = None
    date: str

class TransactionHistoryListOut(BaseModel):
    data: List[InvoiceDetailOut]
