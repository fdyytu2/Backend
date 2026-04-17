import time
import threading
from app.core.logging import logger
from typing import Callable

from fastapi import HTTPException, Request, status
from app.core.config import settings



# Setup Redis Client jika URL tersedia
redis_client = None
try:
    if settings.redis_url:
        import redis
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
except ImportError:
    logger.warning("Library 'redis' belum diinstall. Menggunakan InMemory fallback.")
except Exception as e:
    logger.error(f"Gagal koneksi Redis: {e}. Menggunakan InMemory fallback.")

class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._buckets: dict[str, tuple[int, float]] = {}

    def hit(self, *, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        with self._lock:
            count, start = self._buckets.get(key, (0, now))
            if now - start >= window_seconds:
                count, start = 0, now
            count += 1
            self._buckets[key] = (count, start)

            if count > limit:
                retry_after = max(0, int(window_seconds - (now - start)))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Retry after ~{retry_after}s",
                    headers={"Retry-After": str(retry_after)},
                )

class RedisRateLimiter:
    def hit(self, *, key: str, limit: int, window_seconds: int) -> None:
        if not redis_client:
            raise RuntimeError("Redis client not initialized")
        
        try:
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            result = pipe.execute()
            
            count = result[0]
            ttl = result[1]
            
            if count == 1 or ttl == -1:
                redis_client.expire(key, window_seconds)
            
            if count > limit:
                retry_after = ttl if ttl > 0 else window_seconds
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many requests. Retry after ~{retry_after}s",
                    headers={"Retry-After": str(retry_after)},
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis Rate Limit Error: {e}")
            raise RuntimeError("Fallback")

in_memory_limiter = InMemoryRateLimiter()
redis_limiter = RedisRateLimiter()

def _get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff: return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip")
    if xri: return xri.strip()
    if request.client: return request.client.host
    return "unknown"

def rate_limit(*, prefix: str, limit: int, window_seconds: int = 60) -> Callable:
    async def _dep(request: Request) -> bool:
        client_api_key = request.headers.get("x-api-key")
        if client_api_key and client_api_key == settings.admin_api_key:
            return True

        ip = _get_client_ip(request)
        path = request.url.path
        method = request.method
        key = f"rl:{prefix}:{method}:{path}:{ip}"

        if redis_client:
            try:
                redis_limiter.hit(key=key, limit=limit, window_seconds=window_seconds)
                return True
            except HTTPException:
                raise
            except Exception:
                # 🚩 FALLBACK ke Memory kalau Redis tiba-tiba modar
                in_memory_limiter.hit(key=key, limit=limit, window_seconds=window_seconds)
        else:
            in_memory_limiter.hit(key=key, limit=limit, window_seconds=window_seconds)
        return True

    return _dep
