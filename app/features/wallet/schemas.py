# app/features/wallet/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    currency: str
    available_balance: int
    hold_balance: int
    total_balance: int


class MutationItem(BaseModel):
    created_at: datetime

    journal_id: str
    journal_type: str
    journal_status: str

    reference_id: Optional[str] = None
    description: Optional[str] = None

    account_type: str          # USER_WALLET / HOLDING / SYSTEM
    account_id: str            # wallet_id atau SYSTEM

    direction: str             # DEBIT / CREDIT
    amount: int

    # Pydantic v2
    model_config = {"from_attributes": True}
    # Pydantic v1 fallback:
    # class Config:
    #     orm_mode = True


class MutationsResponse(BaseModel):
    items: list[MutationItem]