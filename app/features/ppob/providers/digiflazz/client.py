import hashlib
from app.shared.http_client import safe_api_request

class DigiflazzClient:
    def __init__(self, username: str, key: str, base_url: str = "https://api.digiflazz.com/v1"):
        self.username = username
        self.key = key
        self.base_url = base_url.rstrip('/')

    def _generate_sign(self, cmd_string: str) -> str:
        return hashlib.md5((self.username + self.key + cmd_string).encode()).hexdigest()

    def get_balance(self) -> dict:
        payload = {"cmd": "deposit", "username": self.username, "sign": self._generate_sign("depo")}
        return safe_api_request("POST", f"{self.base_url}/cek-saldo", json=payload)

    def get_pricelist(self) -> dict:
        payload = {"cmd": "prepaid", "username": self.username, "sign": self._generate_sign("pricelist")}
        return safe_api_request("POST", f"{self.base_url}/price-list", json=payload)

    def check_transaction(self, sku: str, customer_no: str, ref_id: str) -> dict:
        payload = {
            "username": self.username,
            "buyer_sku_code": sku,
            "customer_no": customer_no,
            "ref_id": ref_id,
            "sign": self._generate_sign(ref_id)
        }
        return safe_api_request("POST", f"{self.base_url}/transaction", json=payload)

    # 💡 UPDATE: Sekarang pake SKU "Cek" sesuai arahan Mandor
    def inquiry_pln(self, customer_no: str) -> dict:
        payload = {
            "commands": "inq-pasca",
            "username": self.username,
            "buyer_sku_code": "Cek",
            "customer_no": customer_no,
            "ref_id": f"INQ-{customer_no}",
            "sign": self._generate_sign(f"INQ-{customer_no}")
        }
        return safe_api_request("POST", f"{self.base_url}/transaction", json=payload)
