from app.features.deposit.models import Deposit
from app.core.logging import logger
from app.shared.generators import generate_transaction_id

def create_deposit_invoice(db, user_id: str, amount: int, method: str):
    # 🧱 Gunakan Lego Generator biar ID-nya cantik (DEP-20260409-XXXX)
    internal_id = generate_transaction_id("DEP")
    
    # Simulasi hit API Tripay (Referensi Tripay biasanya unik dari mereka)
    # Tapi kita tetep catat internal_id kita buat tracking
    ref_tripay = f"TRP-{internal_id}" 
    qris_url = f"https://tripay.co.id/qr/{ref_tripay}"

    logger.info(f"[DEPOSIT-INV] 📝 Membuat invoice {internal_id} untuk User {user_id} sebesar Rp{amount}")

    new_deposit = Deposit(
        id=internal_id,
        user_id=user_id,
        amount=amount,
        payment_method=method,
        reference=ref_tripay,
        status="UNPAID"
    )
    
    try:
        db.add(new_deposit)
        db.commit()
        return {
            "deposit_id": internal_id,
            "reference": ref_tripay,
            "amount": amount,
            "checkout_url": qris_url
        }
    except Exception as e:
        db.rollback()
        logger.error(f"[DEPOSIT-INV] ❌ Gagal membuat invoice: {e}")
        raise
