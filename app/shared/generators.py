import random
import string
from app.shared.time import now_utc

def generate_transaction_id(prefix: str = "TRX") -> str:
    """
    Bikin ID transaksi cantik. 
    Contoh hasil: TRX-20260409-X9Y2
    """
    # Ambil tanggal hari ini (contoh: 20260409)
    date_str = now_utc().strftime("%Y%m%d")
    
    # Bikin 4 karakter acak (huruf besar + angka)
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"{prefix}-{date_str}-{random_str}"
