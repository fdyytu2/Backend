from functools import lru_cache
from .app_settings import AppSettings
from .db_settings import DbSettings
from .auth_settings import AuthSettings
from .vendor_settings import VendorSettings

class Settings(AppSettings, DbSettings, AuthSettings, VendorSettings):
    pass

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
