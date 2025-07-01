"""Application settings loaded from the environment using Pydantic."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal, List

from dotenv import load_dotenv
from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration validated by Pydantic."""

    ENVIRONMENT: Literal["dev", "work", "prod"] = "dev"

    GLPI_BASE_URL: HttpUrl = "https://localhost/glpi/apirest.php"
    GLPI_APP_TOKEN: SecretStr = SecretStr("your_app_token")
    GLPI_USERNAME: str = "glpi_user"
    GLPI_PASSWORD: str = "glpi_password"
    GLPI_USER_TOKEN: SecretStr | None = None

    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "glpi_dashboard"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL_SECONDS: int = 3600

    FETCH_PAGE_SIZE: int = 50
    MV_REFRESH_INTERVAL_MINUTES: int = 5

    USE_MOCK_DATA: bool = False
    ALLOWED_IPS: List[str] = []

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    # `load_dotenv()` ensures local development loads variables from `.env` even
    # when Pydantic settings are cached across imports.
    load_dotenv()
    return Settings()


settings = get_settings()

GLPI_BASE_URL = str(settings.GLPI_BASE_URL)
GLPI_APP_TOKEN = settings.GLPI_APP_TOKEN.get_secret_value()
GLPI_USERNAME = settings.GLPI_USERNAME
GLPI_PASSWORD = settings.GLPI_PASSWORD
GLPI_USER_TOKEN = (
    settings.GLPI_USER_TOKEN.get_secret_value() if settings.GLPI_USER_TOKEN else None
)

DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB
REDIS_TTL_SECONDS = settings.REDIS_TTL_SECONDS

FETCH_PAGE_SIZE = settings.FETCH_PAGE_SIZE
MV_REFRESH_INTERVAL_MINUTES = settings.MV_REFRESH_INTERVAL_MINUTES

USE_MOCK_DATA = settings.USE_MOCK_DATA