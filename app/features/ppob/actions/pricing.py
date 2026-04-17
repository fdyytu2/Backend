def calculate_hybrid_split(product_price: int, current_balance: int, use_paylater: bool):
    paylater_margin = 2500 if use_paylater else 0
    total_price = product_price + paylater_margin
    
    # Hitung porsi
    if current_balance >= total_price:
        return total_price, 0, total_price # price_to_pay, shortfall, amount_from_saldo
    
    if not use_paylater:
        return total_price, total_price - current_balance, 0 # Akan trigger error saldo kurang
        
    shortfall = total_price - current_balance
    return total_price, shortfall, current_balance
