import time
import hmac
import hashlib
from fastapi import Request, HTTPException, Header
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

# --- 1. RATE LIMITER (ANTI BRUTE-FORCE / DDOS) ---
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.ip_records = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Bersihin record IP yang umurnya lebih dari 1 detik
        self.ip_records[client_ip] = [t for t in self.ip_records.get(client_ip, []) if now - t < 1]
        
        # Limit 10 request per detik per IP
        if len(self.ip_records[client_ip]) >= 10:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests! Sabar bos, server lagi napas."})
            
        self.ip_records[client_ip].append(now)
        return await call_next(request)

# --- 2. WEBHOOK SIGNATURE (ANTI MALING SALDO) ---
# Ganti ini pakai Secret Key asli dari Digiflazz/Payment Gateway lu nanti!
WEBHOOK_SECRET = "RAHASIA_NEGARA_123" 

async def verify_webhook_signature(request: Request, x_hub_signature: str = Header(None)):
    payload = await request.body()
    secret = WEBHOOK_SECRET.encode('utf-8')
    
    # Contoh pakai HMAC SHA1 (Standar umum webhook)
    expected_sig = hmac.new(secret, payload, hashlib.sha1).hexdigest()
    
    # Kalau header signature kosong atau gak cocok, TENDANG!
    if not x_hub_signature or not hmac.compare_digest(f"sha1={expected_sig}", x_hub_signature):
        raise HTTPException(status_code=403, detail="AKSES DITOLAK! Tanda tangan palsu, dasar hacker!")

import os
import json
from fastapi.responses import JSONResponse

MAINTENANCE_FILE = "maintenance_mode.json"

class MaintenanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # PINTU RAHASIA: Biarin jalur Admin tetep buka biar lu bisa matiin maintenance-nya nanti
        if request.url.path.startswith("/api/v1/admin") or request.url.path.endswith("/docs") or request.url.path.endswith("/openapi.json"):
            return await call_next(request)

        # Kalau file gemboknya ada, bekukan semua request user!
        if os.path.exists(MAINTENANCE_FILE):
            try:
                with open(MAINTENANCE_FILE, "r") as f:
                    data = json.load(f)
                    if data.get("is_frozen"):
                        return JSONResponse(
                            status_code=503,
                            content={"detail": data.get("message", "Sistem sedang dalam perbaikan. Mohon tunggu beberapa saat lagi!")}
                        )
            except Exception:
                pass
        
        return await call_next(request)
