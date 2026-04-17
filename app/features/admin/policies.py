from fastapi import HTTPException
from app.features.users.models import User
from app.core.logging import logger

def check_super_admin_policy(admin: User):
    """
    Hanya mengizinkan Super Admin (User ID tertentu atau level tertinggi).
    Biasa dipakai untuk fitur cetak duit atau freeze system.
    """
    # Ganti dengan kriteria Super Admin lo, misal berdasarkan ID atau flag khusus
    if not admin.is_admin: # Tambahkan logika tambahan jika ada level admin
        logger.warning(f"[POLICY] 🚨 Akses Dewa ditolak untuk Admin: {admin.username}")
        raise HTTPException(status_code=403, detail="Akses ditolak: Hanya untuk Super Admin!")
    
    logger.info(f"[POLICY] ✅ Akses Dewa diberikan untuk: {admin.username}")
    return True

def can_manage_finance(admin: User):
    """Cek apakah admin punya wewenang ngurusin duit/biaya."""
    # Contoh: Semua admin boleh, tapi dicatat di CCTV
    logger.info(f"[POLICY] 💸 Akses keuangan diakses oleh: {admin.username}")
    return True
