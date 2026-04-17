from app.core.logging import logger

def execute_transfer(db, sender_id, receiver_phone, amount, pin):
    logger.info(f"User {sender_id} mencoba transfer Rp{amount} ke {receiver_phone}")
    # Logic validasi dan potong saldo diletakkan di sini nantinya
    return {"status": "success", "message": f"Berhasil transfer ke {receiver_phone}"}
