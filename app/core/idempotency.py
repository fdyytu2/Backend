from sqlalchemy.orm import Session
# Simpan logic pengecekan key transaksi di sini nanti
def check_idempotency(db: Session, key: str):
    pass
