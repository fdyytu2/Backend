import hashlib
import hmac
import secrets
from datetime import timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.features.auth.otp_models import UserOTP

# 🧱 Import Lego dari Kotak Perkakas & Ruang Mesin
from app.core.logging import logger
from app.shared.time import now_utc
from app.shared.http_client import safe_api_request

# --- HELPER FUNCTIONS ---
def _generate_otp() -> str:
    return str(secrets.randbelow(1_000_000)).zfill(6)

def _hash_otp(purpose: str, channel: str, target: str, user_id: str, otp: str) -> str:
    pepper = (settings.otp_secret or settings.jwt_secret).encode("utf-8")
    msg = f"{purpose}|{channel}|{target}|{user_id}|{otp}".encode("utf-8")
    return hmac.new(pepper, msg, hashlib.sha256).hexdigest()

def _mask_target(channel: str, target: str) -> str:
    if channel == "phone":
        return "***" if len(target) <= 6 else f"{target[:4]}****{target[-3:]}"
    if channel == "email" and "@" in target:
        name, dom = target.split("@", 1)
        return f"{name[:1]}***@{dom}" if name else f"***@{dom}"
    return "***"

def _ensure_tz(dt):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

# --- CORE LOGIC (DB) ---
class OtpService:
    def __init__(self, db: Session):
        self.db = db

    def request_otp(self, user_id: str, purpose: str, channel: str, target: str, ttl_seconds: int = 300, cooldown_seconds: int = 60) -> str:
        now = now_utc()

        last_otp = self.db.query(UserOTP).filter_by(
            user_id=user_id, purpose=purpose, channel=channel, target=target
        ).order_by(UserOTP.created_at.desc()).first()

        if last_otp and (now - _ensure_tz(last_otp.created_at)).total_seconds() < cooldown_seconds:
            logger.warning(f"[OTP] ⏳ Cooldown aktif untuk {target} ({purpose})")
            raise HTTPException(status_code=429, detail="Terlalu banyak request. Tunggu sebentar.")

        self.db.query(UserOTP).filter_by(
            user_id=user_id, purpose=purpose, channel=channel, target=target, consumed_at=None
        ).update({"consumed_at": now}, synchronize_session=False)

        otp_code = _generate_otp()
        new_otp = UserOTP(
            user_id=user_id, purpose=purpose, channel=channel, target=target,
            otp_hash=_hash_otp(purpose, channel, target, user_id, otp_code),
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        self.db.add(new_otp)

        try:
            self.db.commit()
            return otp_code
        except SQLAlchemyError:
            self.db.rollback()
            logger.error(f"[OTP] ❌ Gagal simpan OTP ke DB untuk {target}")
            raise HTTPException(status_code=500, detail="Gagal membuat OTP")

    def verify_otp(self, user_id: str, purpose: str, channel: str, target: str, otp: str) -> None:
        now = now_utc()

        row = self.db.query(UserOTP).filter_by(
            user_id=user_id, purpose=purpose, channel=channel, target=target, consumed_at=None
        ).order_by(UserOTP.created_at.desc()).first()

        if not row:
            raise HTTPException(status_code=400, detail="OTP tidak valid atau tidak ditemukan")

        if now > _ensure_tz(row.expires_at):
            row.consumed_at = now
            self.db.commit()
            raise HTTPException(status_code=400, detail="OTP sudah kadaluarsa")

        if row.attempts >= row.max_attempts:
            row.consumed_at = now
            self.db.commit()
            raise HTTPException(status_code=400, detail="OTP diblokir karena terlalu sering salah")

        actual_hash = _hash_otp(purpose, channel, target, user_id, otp)
        if not hmac.compare_digest(row.otp_hash, actual_hash):
            row.attempts += 1
            self.db.commit()
            logger.warning(f"[OTP] ❌ Salah tebak OTP. Percobaan: {row.attempts}/{row.max_attempts}")
            raise HTTPException(status_code=400, detail="Kode OTP salah")

        row.consumed_at = now
        self.db.commit()
        logger.info(f"[OTP] ✅ OTP sukses diverifikasi untuk {_mask_target(channel, target)}")


# --- EXTERNAL SENDER (CLEAN ARCHITECTURE) ---
class OtpNotifier:
    def __init__(self, provider_url: str | None = None):
        self.provider_url = (provider_url or getattr(settings, 'otp_provider_url', '')).strip()

    def send(self, channel: str, target: str, otp: str, purpose: str) -> None:
        masked = _mask_target(channel, target)
        title = f"OTP - {purpose}"
        message = f"Kode OTP Keamanan Anda adalah: {otp}"

        # 🚀 STRATEGY PATTERN: Pilih Provider Berdasarkan Environment
        if settings.env != "production":
            # Mode Development: Gunakan ConsoleProvider resmi dari folder notifications
            from app.features.notifications.providers.console import ConsoleNotificationProvider
            print(f"\n🔥 [LOG-DARURAT] KODE OTP: {otp} \n"); logger.info(f"[OTP-DEV] 🛠️ Mengalihkan ke ConsoleProvider untuk {masked}")
            
            provider = ConsoleNotificationProvider()
            provider.send(to=target, title=title, message=message)
            return

        # Mode Production: Tembak ke API Vendor sungguhan
        if not self.provider_url:
            logger.error(f"[OTP-PROD] 🚨 URL Provider kosong! Gagal kirim OTP ke {masked}")
            return

        payload = {"channel": channel, "target": target, "otp": otp, "purpose": purpose}
        logger.info(f"[OTP-PROD] 🚀 Mengirim payload OTP ke vendor untuk {masked}...")
        
        response = safe_api_request("POST", self.provider_url, json=payload, timeout=5)

        if response and response.get("success"):
            logger.info(f"[OTP-PROD] ✅ OTP sukses terkirim ke vendor untuk {masked}")
        else:
            logger.error(f"[OTP-PROD] ❌ Gagal kirim OTP ke vendor: {response}")
