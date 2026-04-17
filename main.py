from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.middleware import CorrelationIdMiddleware
from app.core.logging import logger

app = FastAPI(title="PPOB Super App", version="1.0.0")

# 🧱 PASANG SATPAM CORS (Biar bebas dari 405 Method Not Allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Izinkan semua domain (buat testing)
    allow_credentials=True,
    allow_methods=["*"],     # Izinkan semua method (termasuk OPTIONS)
    allow_headers=["*"],     # Izinkan semua header
)

# Pasang Pos Satpam di depan
app.add_middleware(CorrelationIdMiddleware)

# Pasang Rute/Jalan Utama
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    logger.info("🚀 Server PPOB Berhasil Menyala!")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Server PPOB Dimatikan.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
