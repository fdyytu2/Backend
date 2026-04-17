from app.core.logging import logger
from app.features.topup.models import Topup, TopupStatus
from app.shared.generators import generate_transaction_id

def process_topup_request(db, user_id: str, amount: int, payment_method: str):
    # 🧱 Gunakan Generator biar ID-nya rapi: TOP-20260409-XXXX
    topup_id = generate_transaction_id("TOP")
    logger.info(f"[TOPUP-REQ] 📥 User {user_id} request manual Rp{amount} via {payment_method}")

    # Buat record di database dengan status PENDING
    new_topup = Topup(
        id=topup_id,
        user_id=user_id,
        amount=amount,
        payment_method=payment_method,
        status=TopupStatus.PENDING,
        ref_id=f"MANUAL-{topup_id}" # Penanda ini transaksi manual
    )

    # 💡 Tips: Data rekening ini nantinya bisa lo ambil dari tabel 'Settings' di DB
    rekening_info = {
        "DANA": "0812-xxxx-xxxx (A/N Nama Lo)",
        "OVO": "0812-xxxx-xxxx (A/N Nama Lo)",
        "BCA": "1234567890 (A/N Nama Lo)"
    }

    try:
        db.add(new_topup)
        db.commit()
        return {
            "topup_id": topup_id,
            "amount": amount,
            "status": "PENDING",
            "instruction": f"Silahkan transfer ke {payment_method}: {rekening_info.get(payment_method, 'Hubungi Admin')}",
            "message": "Segera lakukan pembayaran dan kirim bukti ke Admin."
        }
    except Exception as e:
        db.rollback()
        logger.error(f"[TOPUP-REQ] ❌ Gagal membuat request topup: {e}")
        raise
