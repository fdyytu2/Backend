# app/features/transfers/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ResolvePhoneRequest(BaseModel):
    """Schema untuk request pengecekan nomor HP sebelum transfer"""
    phone: str = Field(..., min_length=8, max_length=20, examples=["08123456789"])


class ResolvePhoneResponse(BaseModel):
    """Schema untuk hasil pengecekan nomor HP"""
    exists: bool
    user_id: Optional[str] = None
    display_name: Optional[str] = None # Nama yang sudah di-masking, misal: "Budi S***"
    phone: Optional[str] = None 


class TransferCreateRequest(BaseModel):
    """Schema untuk eksekusi transfer"""
    receiver_phone: str = Field(..., min_length=8, max_length=20)
    amount: int = Field(..., gt=0)
    pin: str = Field(..., min_length=6, max_length=6)
    note: Optional[str] = Field(None, max_length=255)
    
    # ref_id dari client untuk tracking side-by-side
    ref_id: Optional[str] = Field(None, min_length=3, max_length=50)


class TransferResponse(BaseModel):
    """Schema response setelah transfer berhasil/diproses"""
    id: str
    ref_id: str
    status: str
    amount: int
    fee_amount: int
    sender_user_id: str
    receiver_user_id: str
    journal_id: Optional[str] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransferHistoryFilter(BaseModel):
    """Schema untuk query parameters di history transaksi"""
    limit: int = Field(10, le=100)
    offset: int = 0
    status: Optional[str] = None
