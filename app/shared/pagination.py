from typing import Generic, TypeVar, List, Any
from pydantic import BaseModel
from sqlalchemy.orm import Query

# T ini ibarat "bungkusan kosong" (Generic) yang nanti bisa diisi 
# model data apa aja (bisa data Mutasi, data User, atau data Produk).
T = TypeVar("T")

# 1. Cetakan Standar buat dikirim ke HP User (Front-End)
class PaginatedResponse(BaseModel, Generic[T]):
    total: int          # Total keseluruhan data di database
    limit: int          # Maksimal data per halaman (misal: 20)
    offset: int         # Mulai dari baris ke berapa (misal: 0, 20, 40)
    items: List[T]      # Isi datanya

# 2. Alat Bantu buat motong data di Database (Back-End)
def apply_pagination(query: Query, offset: int = 0, limit: int = 20) -> tuple[int, List[Any]]:
    """
    Fungsi ini bakal ngitung total baris keseluruhan,
    lalu memotong data sesuai limit dan offset yang diminta user.
    """
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return total, items
