"""
Digiflazz Response Parser - Infrastructure Layer
Translates raw Digiflazz API responses into standardized internal structures.
"""
import json

from app.core.logging import logger


# ---------------------------------------------------------------------------
# Response Code Mapping
# ---------------------------------------------------------------------------

RC_MAP: dict[str, str] = {
    "00": "Transaction Successful",
    "01": "Timeout (check mutation)",
    "02": "Transaction Failed",
    "03": "Transaction Pending",
    "40": "Payload Error: invalid data type",
    "41": "Invalid Signature: check API Key & Username",
    "42": "Username mismatch",
    "43": "SKU not found / inactive",
    "44": "Insufficient vendor balance",
    "45": "IP not whitelisted on Digiflazz",
    "49": "Ref ID is not unique",
    "83": "Inquiry limit reached (1 per 5 minutes)",
    "99": "DF Router Issue (Pending)",
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class DigiflazzParser:
    """Parses Digiflazz API responses into normalized dicts."""

    @staticmethod
    def parse_balance_response(response: dict) -> dict:
        """
        Parse cek-saldo response.

        Returns::
            {"status": "success", "balance": int, "message": str}
            {"status": "error",   "message": str, "rc": str | None}
        """
        logger.debug("[DIGIFLAZZ] balance raw: %s", json.dumps(response))

        if not response.get("success"):
            return {"status": "error", "message": response.get("error", "Timeout/Down")}

        http_data = response.get("data", {})
        df_data = http_data.get("data", {})

        if "deposit" in df_data:
            logger.info("[DIGIFLAZZ] Balance check OK: %s", df_data["deposit"])
            return {"status": "success", "balance": df_data["deposit"], "message": "OK"}

        raw_rc = df_data.get("rc")
        rc = str(raw_rc) if raw_rc is not None else None
        msg = RC_MAP.get(rc or "", df_data.get("message", "Unknown vendor format"))
        logger.warning("[DIGIFLAZZ] Balance error RC=%s msg=%s", rc, msg)
        return {"status": "error", "message": msg, "rc": rc}

    @staticmethod
    def parse_transaction_response(response: dict) -> dict:
        """
        Parse transaction response.

        Returns::
            {
                "status": "success" | "error",
                "mapped_status": "SUCCESS" | "FAILED" | "PENDING",
                "vendor_status": str,
                "sn": str,
                "message": str,
                "rc": str,
            }
        """
        logger.debug("[DIGIFLAZZ] transaction raw: %s", json.dumps(response))

        if not response.get("success"):
            return {"status": "error", "message": response.get("error", "Unknown")}

        http_data = response.get("data", {})
        data = http_data.get("data", {})

        if not data:
            return {"status": "error", "message": "No data from vendor"}

        rc = str(data.get("rc", ""))
        vendor_status = str(data.get("status", "")).upper()
        sn = data.get("sn", "")
        message = data.get("message", RC_MAP.get(rc, "Unknown vendor message"))

        # Map to internal status
        if vendor_status in ("SUKSES", "SUCCESS") or rc == "00":
            mapped_status = "SUCCESS"
        elif vendor_status in ("GAGAL", "FAILED") or rc in (
            "02", "40", "41", "42", "43", "44", "45", "49"
        ):
            mapped_status = "FAILED"
        else:
            mapped_status = "PENDING"

        return {
            "status": "success",
            "mapped_status": mapped_status,
            "vendor_status": vendor_status,
            "sn": sn,
            "message": message,
            "rc": rc,
        }

    @staticmethod
    def parse_pricelist_item(item: dict) -> dict:
        """Normalize a single pricelist item from Digiflazz."""
        vendor_status_raw = str(item.get("seller_product_status", "")).lower()
        is_active = vendor_status_raw in ("normal", "1", "true", "lancar")
        return {
            "sku_code": item.get("buyer_sku_code"),
            "name": item.get("product_name"),
            "category": (item.get("category") or "").upper(),
            "brand": (item.get("brand") or "").upper(),
            "type": (item.get("type") or "").upper(),
            "price_base": int(item.get("price") or 0),
            "is_active_provider": is_active,
        }
