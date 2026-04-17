import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import request_id_var, logger

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 1. Satpam nyetak Nomor Resi Unik (Contoh: REQ-A1B2C)
        req_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"
        
        # 2. Titipin resinya ke memori CCTV
        token = request_id_var.set(req_id)
        
        # Lapor ke terminal kalau ada tamu masuk
        logger.info(f"Incoming Request: {request.method} {request.url.path}")
        
        # 3. Suruh tamu masuk ke dalam (proses API)
        response = await call_next(request)
        
        # 4. Tambahin Nomor Resi di struk balasan (Biar frontend tau)
        response.headers["X-Request-ID"] = req_id
        
        # Lapor kalau tamu udah selesai
        logger.info(f"Completed Request with status {response.status_code}")
        
        # Bersihin memori
        request_id_var.reset(token)
        
        return response
