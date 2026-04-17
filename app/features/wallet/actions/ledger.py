from app.core.logging import logger
from app.features.wallet.enums import AccountType, JournalStatus, LedgerDirection
from app.features.wallet.repository import WalletRepository

def post_ledger_entry(db, *, journal_type, idempotency_key, amount, 
                     debit_id, credit_id, debit_type=AccountType.USER, 
                     credit_type=AccountType.USER, release_hold=0, 
                     ref_id=None, description=None): # 💡 Ditambahin description di sini
    
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    repo = WalletRepository(db)
    
    # Cek Idempotency (Anti-Double Hit)
    existing = repo.get_journal_by_idempotency(idempotency_key)
    if existing:
        return existing.id

    try:
        with db.begin_nested():
            # 1. Lock baris dompet biar gak bentrok
            a_ids = sorted([debit_id, credit_id])
            wallets = {aid: repo.lock_wallet_row(aid) for aid in a_ids}
            
            # 2. Validasi Saldo
            sender = wallets[debit_id]
            if debit_type == AccountType.USER:
                hold = getattr(sender, 'hold_balance', 0)
                if release_hold > 0:
                    sender.hold_balance = hold - release_hold
                elif (sender.balance - hold) < amount:
                    raise ValueError("Insufficient funds")

            # 3. Catat Jurnal (Sekarang bawa description)
            journal = repo.create_journal(
                type=journal_type.value, 
                status=JournalStatus.SUCCESS.value,
                idempotency_key=idempotency_key, 
                reference_id=ref_id,
                description=description # 💡 Masukin ke catatan jurnal
            )
            db.flush()

            # 4. Catat Entry
            repo.add_entry(
                journal_id=journal.id, 
                account_type=debit_type.value, 
                account_id=debit_id, 
                direction=LedgerDirection.DEBIT.value, 
                amount=amount
            )
            repo.add_entry(
                journal_id=journal.id, 
                account_type=credit_type.value, 
                account_id=credit_id, 
                direction=LedgerDirection.CREDIT.value, 
                amount=amount
            )

            # 5. Update Balance Real-time
            wallets[debit_id].balance -= amount
            wallets[credit_id].balance += amount
            
            db.flush()
            return journal.id
            
    except Exception as e:
        logger.error(f"[LEDGER-FATAL] {e}")
        raise RuntimeError(str(e))
