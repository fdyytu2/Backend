from pydantic_settings import BaseSettings
from pydantic import Field

class AuthSettings(BaseSettings):
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", alias="JWT_ALG")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    otp_secret: str | None = Field(default=None, alias="OTP_SECRET")
    otp_provider_url: str = Field(default="", alias="OTP_PROVIDER_URL")
    admin_api_key: str = Field(default="change-me-admin-key", alias="ADMIN_API_KEY")
    
    # 🔐 Tambahan Keamanan: Gembok Otomatis
    login_max_attempts: int = Field(default=5, alias="LOGIN_MAX_ATTEMPTS")
    login_lock_minutes: int = Field(default=15, alias="LOGIN_LOCK_MINUTES")
