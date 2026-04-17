import logging
from typing import Any

logger = logging.getLogger("app.notifications")

class DummyHttpOtpProvider:
    def __init__(self, base_url: str | None):
        self.base_url = (base_url or "").strip()

    async def send(self, *, channel: str, target: str, otp: str, purpose: str) -> None:
        # Kalau base_url kosong, anggap sukses tapi tetap log
        if not self.base_url:
            logger.info("otp_dummy_api channel=%s target=%s purpose=%s otp=%s", channel, target, purpose, otp)
            return

        # Nanti production: kirim beneran via httpx ke endpoint provider kamu
        logger.info("otp_api_send channel=%s target=%s purpose=%s base_url=%s", channel, target, purpose, self.base_url)