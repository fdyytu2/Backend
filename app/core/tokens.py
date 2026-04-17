from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

def create_access_token(subject: str):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

def decode_access_token(token: str):
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
