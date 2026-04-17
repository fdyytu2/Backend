# app/shared/phone.py
import re

def normalize_id_phone(raw: str) -> str:
    """
    Normalisasi nomor Indonesia ke format +62xxxxxxxxxxx.
    Input contoh: 0812..., 62812..., +62812..., pakai spasi/strip juga aman.
    """
    if raw is None:
        return ""

    s = raw.strip()
    s = s.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    s = re.sub(r"[^\d+]", "", s)

    if s.startswith("08"):
        return "+62" + s[1:]   # buang 0 depan

    if s.startswith("8"):
        return "+62" + s       # kalau user input 8123...

    if s.startswith("62"):
        return "+" + s         # 62xxx -> +62xxx

    if s.startswith("+62"):
        return s

    return s


# Alias biar konsisten dipakai seluruh app
def normalize_phone(raw: str) -> str:
    return normalize_id_phone(raw)