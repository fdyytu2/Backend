# app/core/http_logging.py
import logging
import time
from typing import Iterable

from starlette.types import ASGIApp, Receive, Scope, Send


def _get_header(scope: Scope, name: bytes) -> str | None:
    for k, v in scope.get("headers", []):
        if k.lower() == name:
            try:
                return v.decode("latin-1")
            except Exception:
                return None
    return None


def _get_client_ip(scope: Scope) -> str:
    # Prioritas: X-Forwarded-For -> X-Real-IP -> scope.client
    xff = _get_header(scope, b"x-forwarded-for")
    if xff:
        # Format bisa: "ip1, ip2, ip3"
        return xff.split(",")[0].strip()

    xri = _get_header(scope, b"x-real-ip")
    if xri:
        return xri.strip()

    client = scope.get("client")
    if client and len(client) >= 1:
        return str(client[0])

    return "unknown"


class HttpAccessLogMiddleware:
    """
    Access log versi aplikasi (bukan uvicorn.access), lebih detail dan konsisten
    dengan formatter logging kamu.

    Catatan keamanan:
    - Jangan log request body (password/token bisa kebaca).
    - Query string juga bisa sensitif; default: tidak dilog.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        logger_name: str = "app.http",
        skip_paths: Iterable[str] = ("/health",),
        log_query_string: bool = False,
    ) -> None:
        self.app = app
        self.logger = logging.getLogger(logger_name)
        self.skip_paths = set(skip_paths)
        self.log_query_string = log_query_string

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self.skip_paths:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "-")
        ip = _get_client_ip(scope)
        ua = _get_header(scope, b"user-agent") or "-"

        qs = ""
        if self.log_query_string:
            raw_qs = scope.get("query_string", b"")
            try:
                qs = raw_qs.decode("utf-8", errors="replace")
            except Exception:
                qs = ""

        start = time.perf_counter()
        status_code = 500
        errored = False

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            errored = True
            duration_ms = (time.perf_counter() - start) * 1000.0

            # exception() akan print traceback lengkap
            self.logger.exception(
                "request_failed method=%s path=%s status=%s duration_ms=%.2f ip=%s ua=%r%s",
                method,
                path,
                500,
                duration_ms,
                ip,
                ua,
                f" qs={qs!r}" if self.log_query_string else "",
            )
            raise
        finally:
            # Kalau sudah error dan sudah dilog via exception(), jangan dobel log
            if not errored:
                duration_ms = (time.perf_counter() - start) * 1000.0

                # level log berdasarkan status
                if status_code >= 500:
                    log_fn = self.logger.error
                elif status_code >= 400:
                    log_fn = self.logger.warning
                else:
                    log_fn = self.logger.info

                log_fn(
                    "request method=%s path=%s status=%s duration_ms=%.2f ip=%s ua=%r%s",
                    method,
                    path,
                    status_code,
                    duration_ms,
                    ip,
                    ua,
                    f" qs={qs!r}" if self.log_query_string else "",
                )