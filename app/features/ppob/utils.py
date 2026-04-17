import re
from typing import Optional

# Mapping Prefix ke Brand sesuai standar industri PPOB Indonesia
# Data ini mencakup update terbaru (termasuk By.U di bawah Telkomsel)
OPERATOR_PREFIXES = {
    "TELKOMSEL": r"^(0811|0812|0813|0821|0822|0823|0852|0853|0851)",
    "INDOSAT": r"^(0814|0815|0816|0855|0856|0857|0858)",
    "XL": r"^(0817|0818|0819|0859|0877|0878)",
    "AXIS": r"^(0831|0832|0833|0838)",
    "TRI": r"^(0895|0896|0897|0898|0899)",
    "SMARTFREN": r"^(0881|0882|0883|0884|0885|0886|0887|0888|0889)",
}

def detect_operator(phone_number: str) -> Optional[str]:
    """
    Mendeteksi brand operator berdasarkan prefix nomor HP.
    Input: '08123456789'
    Output: 'TELKOMSEL' atau None jika tidak dikenal.
    """
    # Bersihkan nomor dari karakter non-digit (spasi, dash, dll)
    clean_phone = re.sub(r"\D", "", phone_number)

    # Validasi panjang nomor HP Indonesia (10-14 digit)
    if not (10 <= len(clean_phone) <= 14):
        return None

    for brand, pattern in OPERATOR_PREFIXES.items():
        if re.match(pattern, clean_phone):
            return brand
            
    return None

def validate_phone_with_sku(phone_number: str, sku_brand: str) -> bool:
    """
    Validasi silang: Memastikan nomor HP sesuai dengan Brand SKU yang dibeli.
    Mencegah user beli Pulsa XL tapi masukin nomor Telkomsel.
    """
    detected = detect_operator(phone_number)
    if not detected:
        return False
        
    # SKU Brand biasanya TELKOMSEL, XL, dll (uppercase)
    return detected == sku_brand.upper()
