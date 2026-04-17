import re

def is_valid_pin(pin: str) -> bool:
    """Razia PIN: Harus murni 6 digit angka, nggak boleh kurang/lebih."""
    if not pin:
        return False
    return bool(re.fullmatch(r"\d{6}", pin))

def is_strong_password(password: str) -> bool:
    """
    Razia Password: 
    - Minimal 8 karakter
    - Harus ada minimal 1 huruf BESAR
    - Harus ada minimal 1 angka
    """
    if not password or len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True
