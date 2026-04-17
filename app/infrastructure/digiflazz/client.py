"""
Digiflazz API Client - Infrastructure Layer
Handles all raw HTTP communication with Digiflazz provider.
"""
import hashlib

from app.shared.http_client import safe_api_request


class DigiflazzClient:
    """Low-level HTTP client for the Digiflazz PPOB API."""

    def __init__(self, username: str, key: str, base_url: str = "https://api.digiflazz.com/v1"):
        self.username = username
        self.key = key
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Signature helpers
    # ------------------------------------------------------------------

    def _sign(self, suffix: str) -> str:
        """Generate MD5 signature: md5(username + api_key + suffix)."""
        raw = f"{self.username}{self.key}{suffix}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Public API Methods
    # ------------------------------------------------------------------

    def get_balance(self) -> dict:
        """Check vendor deposit balance."""
        payload = {
            "cmd": "deposit",
            "username": self.username,
            "sign": self._sign("depo"),
        }
        return safe_api_request("POST", f"{self.base_url}/cek-saldo", json=payload)

    def get_pricelist(self) -> dict:
        """Fetch full product pricelist from Digiflazz."""
        payload = {
            "cmd": "prepaid",
            "username": self.username,
            "sign": self._sign("pricelist"),
        }
        return safe_api_request("POST", f"{self.base_url}/price-list", json=payload)

    def create_transaction(self, sku: str, customer_no: str, ref_id: str) -> dict:
        """Submit a new PPOB purchase transaction."""
        payload = {
            "username": self.username,
            "buyer_sku_code": sku,
            "customer_no": customer_no,
            "ref_id": ref_id,
            "sign": self._sign(ref_id),
        }
        return safe_api_request("POST", f"{self.base_url}/transaction", json=payload)

    def check_transaction(self, sku: str, customer_no: str, ref_id: str) -> dict:
        """Check status of an existing transaction (same endpoint as create)."""
        return self.create_transaction(sku, customer_no, ref_id)

    def inquiry_pln(self, customer_no: str) -> dict:
        """Inquiry PLN customer name/info before purchase."""
        ref_id = f"INQ-{customer_no}"
        payload = {
            "commands": "inq-pasca",
            "username": self.username,
            "buyer_sku_code": "Cek",
            "customer_no": customer_no,
            "ref_id": ref_id,
            "sign": self._sign(ref_id),
        }
        return safe_api_request("POST", f"{self.base_url}/transaction", json=payload)
