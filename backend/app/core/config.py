from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = BACKEND_DIR / "data" / "geothermal.db"

class Settings(BaseSettings):
    app_name: str = "地热产能计算 API"
    database_url: str = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
    cors_origins: str = "*"
    jwt_secret_key: str = "change-this-development-secret-key-before-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    snowflake_worker_id: int = Field(default=1, ge=0, le=1023)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
