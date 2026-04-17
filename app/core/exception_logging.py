import traceback
from app.core.logging import logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime



class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            error_msg = f"[{datetime.now()}] ERROR on {request.method} {request.url.path}: {str(e)}\n{traceback.format_exc()}\n"
            # Print ke console
            logger.info(error_msg)
            # Tulis ke file log biar bisa ditarik sama endpoint Admin Dashboard
            with open("app-error.log", "a") as f:
                f.write(error_msg)
            raise e
