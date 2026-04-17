from app.core.logging import logger

def calculate_hybrid_split(product_price: int, current_balance: int, use_paylater: bool):
    """
    Menghitung berapa yang diambil dari Saldo dan berapa dari Paylater.
    """
    paylater_margin = 2500 if use_paylater else 0
    total_to_pay = product_price + paylater_margin
    
    # Default: Semua dari saldo
    amount_from_saldo = total_to_pay
    shortfall = 0

    if current_balance < total_to_pay:
        if not use_paylater:
            logger.warning(f"[PRICING] Saldo Rp{current_balance} tidak cukup untuk bayar Rp{total_to_pay}")
            return total_to_pay, (total_to_pay - current_balance), 0
            
        shortfall = total_to_pay - current_balance
        amount_from_saldo = current_balance
        logger.info(f"[PRICING] Hybrid Aktif: Saldo Rp{amount_from_saldo}, Paylater Rp{shortfall}")
    
    return total_to_pay, shortfall, amount_from_saldo
