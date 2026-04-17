from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import json

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    app_name: str = Field(default="PPOB Backend", alias="APP_NAME")
    env: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    cors_origins_raw: str = Field(default='["*"]', alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        try: return json.loads(self.cors_origins_raw)
        except: return ["*"]
