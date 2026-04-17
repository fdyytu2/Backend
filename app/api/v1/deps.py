from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from app.core.tokens import decode_access_token
from app.core.config import settings
from app.core.db_session import get_db
from app.features.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing sub")
    except ExpiredSignatureError:
        raise _unauthorized("Token expired")
    except (JWTError, ValueError):
        raise _unauthorized("Invalid token")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise _unauthorized("User not found")

    # Kalau user dinonaktifkan
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=403, detail="User disabled")

    return user


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin key invalid")