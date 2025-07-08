"""Application settings loaded from the environment using Pydantic."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration validated by Pydantic."""

    ENVIRONMENT: Literal["dev", "work", "prod"] = "dev"

    GLPI_BASE_URL: str = os.getenv(
        "GLPI_BASE_URL", "https://localhost/glpi/apirest.php"
    )
    GLPI_APP_TOKEN: str = os.getenv("GLPI_APP_TOKEN", "your_app_token")
    GLPI_USERNAME: str = os.getenv("GLPI_USERNAME", "glpi_user")
    GLPI_PASSWORD: str = os.getenv("GLPI_PASSWORD", "glpi_password")
    GLPI_USER_TOKEN: str | None = os.getenv("GLPI_USER_TOKEN", None)  # Optional

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

    knowledge_base_file: str = os.getenv(
        "KNOWLEDGE_BASE_FILE", "docs/knowledge_base_errors.md"
    )
    database_url: str = ""
    redis_url: str = ""
    cache_type: str = ""
    cache_redis_host: str = ""
    cache_redis_port: str = ""
    cache_redis_db: str = ""
    cache_default_timeout: str = ""
    codegpt_plus_api_key: str = ""

    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    OTEL_EXPORTER_OTLP_HEADERS: str | None = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    OTEL_SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "glpi_dashboard_cau")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    # `load_dotenv()` ensures local development loads variables from `.env` even
    # when Pydantic settings are cached across imports.
    load_dotenv()
    return Settings()


settings = get_settings()

GLPI_BASE_URL = str(settings.GLPI_BASE_URL)
GLPI_APP_TOKEN = settings.GLPI_APP_TOKEN
GLPI_USERNAME = settings.GLPI_USERNAME
GLPI_PASSWORD = settings.GLPI_PASSWORD
GLPI_USER_TOKEN = settings.GLPI_USER_TOKEN or None

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

KNOWLEDGE_BASE_FILE = settings.knowledge_base_file

OTEL_EXPORTER_OTLP_ENDPOINT = settings.OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS = settings.OTEL_EXPORTER_OTLP_HEADERS
OTEL_SERVICE_NAME = settings.OTEL_SERVICE_NAME
