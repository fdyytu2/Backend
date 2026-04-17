import hashlib

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def sign_pricelist(username: str, api_key: str) -> str:
    """Signature untuk tarik daftar produk"""
    # Pattern: md5(username + api_key + "pricelist")
    return md5_hex(f"{username}{api_key}pricelist")

def sign_transaction(username: str, api_key: str, ref_id: str) -> str:
    """Signature untuk beli (order) & cek status transaksi"""
    # Pattern: md5(username + api_key + ref_id)
    return md5_hex(f"{username}{api_key}{ref_id}")

def sign_balance(username: str, api_key: str) -> str:
    """Signature untuk cek saldo deposit kita di Digiflazz"""
    # Pattern: md5(username + api_key + "depo")
    return md5_hex(f"{username}{api_key}depo")
