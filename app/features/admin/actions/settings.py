from sqlalchemy.orm import Session
from app.features.admin.models import SystemSetting
from app.core.logging import logger

def get_setting(db: Session, key: str, default: str = "") -> str:
    """Ambil config dari database"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return setting.value if setting else default

def set_setting(db: Session, key: str, value: str, description: str = None):
    """Simpan atau update config ke database"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if setting:
        setting.value = str(value)
        if description: setting.description = description
    else:
        setting = SystemSetting(key=key, value=str(value), description=description)
        db.add(setting)
    
    try:
        db.commit()
        logger.info(f"[CONFIG] ⚙️ Berhasil update {key}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"[CONFIG] ❌ Gagal update {key}: {e}")
        return False

def get_digiflazz_config(db: Session):
    """Shortcut khusus buat ambil semua data Digiflazz"""
    return {
        "username": get_setting(db, "DIGIFLAZZ_USERNAME"),
        "api_key": get_setting(db, "DIGIFLAZZ_API_KEY"),
        "base_url": get_setting(db, "DIGIFLAZZ_BASE_URL", "https://api.digiflazz.com/v1"),
        "mode": get_setting(db, "DIGIFLAZZ_MODE", "DEVELOPMENT")
    }
