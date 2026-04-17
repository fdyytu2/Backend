def format_rupiah(amount: int) -> str:
    return f"Rp{amount:,}".replace(",", ".")
