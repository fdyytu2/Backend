from fastapi import APIRouter

# 📂 Import Semua Resepsionis Fitur
from app.features.auth.routes import router as auth_router
from app.features.users.routes import router as users_router
from app.features.wallet.routes import router as wallet_router
from app.features.ppob.routes import router as ppob_router
from app.features.transfers.routes import router as transfers_router
from app.features.admin.routes import router as admin_router
from app.features.deposit.routes import router as deposit_router
from app.features.topup.routes import router as topup_router
from app.features.paylater.routes import router as paylater_router
from app.features.notifications.routes import router as notifications_router

api_router = APIRouter()

# 🔌 Colokin Kabel Ke Jalur Utama
api_router.include_router(auth_router, prefix="/auth", tags=["🔑 Auth"])
api_router.include_router(users_router, prefix="/users", tags=["👤 Users"])
api_router.include_router(wallet_router, prefix="/wallet", tags=["👛 Wallet"])
api_router.include_router(ppob_router, prefix="/ppob", tags=["🛒 PPOB"])
api_router.include_router(transfers_router, prefix="/transfers", tags=["💸 Transfers"])
api_router.include_router(admin_router, prefix="/admin", tags=["⚡ Admin God Mode"])
api_router.include_router(deposit_router, prefix="/deposit", tags=["💳 Deposit"])
api_router.include_router(topup_router, prefix="/topup", tags=["📥 Topup Manual"])
api_router.include_router(paylater_router, prefix="/paylater", tags=["⌛ Paylater"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["🔔 Notifications"])
