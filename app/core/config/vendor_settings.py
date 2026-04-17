from pydantic_settings import BaseSettings
from pydantic import Field

class VendorSettings(BaseSettings):
    digiflazz_base_url: str = Field(default="https://api.digiflazz.com/v1", alias="DIGIFLAZZ_BASE_URL")
    digiflazz_username: str = Field(default="", alias="DIGIFLAZZ_USERNAME")
    digiflazz_api_key: str = Field(default="", alias="DIGIFLAZZ_API_KEY")
    enable_jobs: bool = Field(default=True, alias="ENABLE_JOBS")
