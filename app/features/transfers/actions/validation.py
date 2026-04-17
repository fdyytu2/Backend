from fastapi import HTTPException
from app.core.hashing import verify_pin

def normalize_transfer_phone(phone: str) -> str:
    if not phone: return phone
    p = phone.strip().replace(" ", "").replace("-", "")
    if p.startswith("+62"): p = "62" + p[3:]
    elif p.startswith("08"): p = "62" + p[1:]
    return "".join(filter(str.isdigit, p))

def validate_transfer_auth(pin: str, hashed_pin: str):
    if not hashed_pin:
        raise HTTPException(status_code=400, detail="PIN belum diatur.")
    if not verify_pin(pin, hashed_pin):
        raise HTTPException(status_code=401, detail="PIN salah.")
