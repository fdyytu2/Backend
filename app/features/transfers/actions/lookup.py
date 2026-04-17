from fastapi import HTTPException
from app.features.users.repository import UserRepository

def find_receiver_by_phone(db, phone: str, sender_id: str):
    users = UserRepository(db)
    receiver = users.get_by_phone(phone)
    if not receiver:
        raise HTTPException(status_code=404, detail="Nomor penerima tidak ditemukan.")
    if str(receiver.id) == str(sender_id):
        raise HTTPException(status_code=400, detail="Tidak bisa transfer ke diri sendiri.")
    return receiver
