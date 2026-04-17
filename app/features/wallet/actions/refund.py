from app.core.logging import logger
from app.features.wallet.actions.holding import release_user_hold
from app.features.wallet.actions.ledger import post_ledger_entry
from app.features.wallet.enums import JournalType, AccountType

SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

def refund_ppob_order(db, user_id: str, amount: int, order_id: str, is_held: bool = True):
    """
    Fungsi cerdas buat balikin duit user kalau transaksi gagal.
    """
    logger.info(f"[WALLET-REFUND] 🔄 Memulai proses refund untuk Order: {order_id}")

    try:
        if is_held:
            # Skenario 1: Duitnya masih di-HOLD (Gagal pas awal)
            # Tinggal kita cairkan biar balik ke saldo aktif
            release_user_hold(db, user_id, amount)
            logger.info(f"[WALLET-REFUND] ✅ Dana HOLD Rp{amount} berhasil dicairkan untuk {order_id}")
        else:
            # Skenario 2: Duit udah kepotong (Gagal setelah sukses di awal)
            # Kita suntik balik saldonya via Ledger
            post_ledger_entry(
                db,
                journal_type=JournalType.REFUND,
                idempotency_key=f"refund-{order_id}",
                amount=amount,
                debit_id=SYSTEM_ACCOUNT_ID,
                debit_type=AccountType.SYSTEM,
                credit_id=user_id, # Asumsi user_id adalah wallet_id
                credit_type=AccountType.USER,
                description=f"Refund Pembatalan Order {order_id}"
            )
            logger.info(f"[WALLET-REFUND] ✅ Saldo Rp{amount} berhasil dikembalikan via Ledger untuk {order_id}")
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"[WALLET-REFUND] ❌ Gagal melakukan refund {order_id}: {e}")
        return False
