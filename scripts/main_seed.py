import sys
import os

# Biar Python ngebaca folder app lu dari root project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db_session import SessionLocal
from app.features.users.models import User
from app.core.hashing import hash_password 
from app.features.wallet.models import Wallet

# 🐛 FIX: Definisikan ID Dewa secara eksplisit karena file wallet.service nggak ada
SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"

def run_all_seeds():
    db = SessionLocal()
    try:
        # -----------------------------------------------------------
        # 1. Bikin SUPER ADMIN dengan ID SISTEM (The One)
        # -----------------------------------------------------------
        admin = db.query(User).filter(User.id == SYSTEM_ACCOUNT_ID).first()
        
        if not admin:
            admin = User(
                id=SYSTEM_ACCOUNT_ID,
                username="admin", 
                phone="6285159163440", 
                email="admin@ppob.com",
                password_hash=hash_password("kentos@12"), 
                is_admin=True,       
                is_active=True, 
                email_verified=True, 
                phone_verified=True
            )
            db.add(admin)
            db.flush() 
            print(f"✅ Auto-Seed: Akun Super Admin ('admin') dengan ID Sistem berhasil dibuat.")
        else:
            print("ℹ️ Auto-Seed: Akun Admin/Sistem sudah ada.")

        # -----------------------------------------------------------
        # 2. Bikin BRANKAS PUSAT (Wallet untuk ID Sistem)
        # -----------------------------------------------------------
        admin_wallet = db.query(Wallet).filter(Wallet.user_id == SYSTEM_ACCOUNT_ID).first()
        
        if not admin_wallet:
            admin_wallet = Wallet(
                id=SYSTEM_ACCOUNT_ID, 
                user_id=SYSTEM_ACCOUNT_ID, 
                balance=0
            )
            db.add(admin_wallet)
            print("✅ Auto-Seed: Brankas Pusat berhasil dibuat.")
        else:
            print("ℹ️ Auto-Seed: Brankas Pusat sudah ada.")

        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Gagal mengeksekusi seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_all_seeds()
