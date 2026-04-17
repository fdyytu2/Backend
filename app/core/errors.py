# app/core/errors.py
import logging
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("app.errors")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 422 biasanya gak perlu traceback
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Log 5xx HTTPException (karena biasanya berasal dari catch internal)
        if exc.status_code >= 500:
            request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
            logger.error(
                "HTTPException_5XX request_id=%s method=%s path=%s detail=%r",
                request_id,
                request.method,
                request.url.path,
                exc.detail,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "request_id": request_id},
                headers={"X-Request-ID": request_id},
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # INI yang kamu butuhin: traceback full
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        logger.exception(
            "UNHANDLED_EXCEPTION request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )