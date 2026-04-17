from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db_session import get_db
from app.api.v1.deps import get_current_user
from app.features.transfers.actions import lookup, execution

router = APIRouter()

@router.post("/lookup")
def transfer_lookup(payload: dict, db: Session = Depends(get_db)):
    """Cek nama penerima sebelum kirim duit."""
    return lookup.find_recipient(db, identifier=payload.get("target"))

@router.post("/execute")
def transfer_execute(payload: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Eksekusi pengiriman saldo antar user."""
    return execution.process_transfer(db, sender_id=current_user.id, payload=payload)
