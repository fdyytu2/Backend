from pydantic_settings import BaseSettings
from pydantic import Field

class DbSettings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    sqlite_path: str = Field(default="./app.db", alias="SQLITE_PATH")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
