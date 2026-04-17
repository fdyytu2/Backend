import sys
import os

# Biar Python ngebaca folder app lu dari root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db_base import Base
from app.core.db_engine import engine

# 🧱 IMPORT SEMUA MODEL (Wajib lengkap!)
from app.features.users.models import User
from app.features.auth.otp_models import UserOTP
from app.features.wallet.models import Wallet, LedgerJournal, LedgerEntry
from app.features.transfers.models import Transfer
from app.features.ppob.models import PPOBProduct, PPOBOrder
from app.features.deposit.models import Deposit
from app.features.admin.models import SystemSetting, Banner, Ticket

# 💡 NEW: Import Model Notifikasi Biar Dibaca Sama SQLAlchemy!
from app.features.notifications.models import Notification

try:
    print("🔨 Menempa ulang tabel yang belum ada di app.db...")
    # create_all tidak akan menghapus data, hanya menambah tabel yang absen
    Base.metadata.create_all(bind=engine)
    print("✅ BUM! Tabel notifications dan lainnya berhasil dipastikan ada.")
except Exception as e:
    print(f"❌ Waduh, ada yang nyangkut: {e}")
