from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.features.wallet.models import Wallet, LedgerEntry, LedgerJournal

# 🧱 Import Lego & CCTV
from app.shared.pagination import apply_pagination
from app.core.logging import logger

def get_user_transaction_history(db: Session, user_id: str, limit: int = 20, offset: int = 0):
    logger.info(f"[WALLET] 📖 Membuka buku tabungan (history) untuk User ID: {user_id}")
    
    # 1. Cari dompet si user
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        logger.warning(f"[WALLET] ❌ Dompet tidak ditemukan untuk User ID {user_id}")
        return {"total": 0, "limit": limit, "offset": offset, "items": []}

    # 2. Bikin Query Dasar: Tarik semua entri yang nyangkut sama dompet ini
    base_query = (
        db.query(LedgerEntry, LedgerJournal)
        .join(LedgerJournal, LedgerEntry.journal_id == LedgerJournal.id)
        .filter(LedgerEntry.account_id == wallet.id)
        .order_by(desc(LedgerEntry.created_at))
    )

    # 3. ✂️ EKSEKUSI LEGO: Potong data pakai mesin pemotong halaman
    total_data, entries = apply_pagination(base_query, offset=offset, limit=limit)

    # 4. Rakit datanya biar rapi pas dikirim ke HP / Frontend
    history_items = []
    for entry, journal in entries:
        history_items.append({
            "transaction_id": journal.reference_id or journal.id,
            "type": journal.type,              # Contoh: TOPUP, PPOB, TRANSFER
            "status": journal.status,          # Contoh: COMPLETED, PENDING
            "direction": entry.direction,      # CREDIT (Masuk) / DEBIT (Keluar)
            "amount": entry.amount,
            "description": journal.description,
            "created_at": entry.created_at.isoformat()
        })

    logger.info(f"[WALLET] ✅ Berhasil menarik {len(history_items)} baris dari total {total_data} transaksi.")
    
    return {
        "total": total_data,
        "limit": limit,
        "offset": offset,
        "items": history_items
    }
