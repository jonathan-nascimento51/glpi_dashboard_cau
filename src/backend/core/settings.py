"""Application settings loaded from the environment using Pydantic."""

from __future__ import annotations

import contextlib
import os
from functools import lru_cache
from typing import Literal, cast

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_or_file(key: str, default: str | None = None) -> str | None:
    """Return value from ``key`` or read the path in ``key_FILE`` if present."""
    if file_var := os.getenv(f"{key}_FILE"):
        with contextlib.suppress(OSError):
            with open(file_var, "r", encoding="utf-8") as fh:
                return fh.read().strip()
    return os.getenv(key, default)


class Settings(BaseSettings):
    """Central configuration validated by Pydantic."""

    ENVIRONMENT: Literal["dev", "work", "prod"] = "dev"

    GLPI_BASE_URL: str = cast(str, os.getenv("GLPI_BASE_URL", ""))
    GLPI_APP_TOKEN: str = cast(str, _env_or_file("GLPI_APP_TOKEN", "your_app_token"))
    GLPI_USERNAME: str = os.getenv("GLPI_USERNAME", "glpi_user")
    GLPI_PASSWORD: str = cast(str, _env_or_file("GLPI_PASSWORD", "glpi_password"))
    GLPI_USER_TOKEN: str | None = _env_or_file("GLPI_USER_TOKEN", None)  # Optional

    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "glpi_dashboard"
    DB_USER: str = "user"
    DB_PASSWORD: str = cast(str, _env_or_file("DB_PASSWORD", "password"))

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL_SECONDS: int = 3600

    EVENT_BROKER_URL: str = os.getenv("EVENT_BROKER_URL", "localhost:9092")

    FETCH_PAGE_SIZE: int = 50
    MV_REFRESH_INTERVAL_MINUTES: int = 5

    USE_MOCK_DATA: bool = False

    VERIFY_SSL: bool = True
    CLIENT_TIMEOUT_SECONDS: int = 30
    DASH_PORT: int = int(os.getenv("DASH_PORT", "8050"))

    knowledge_base_file: str = os.getenv(
        "KNOWLEDGE_BASE_FILE", "docs/knowledge_base_errors.md"
    )
    mock_tickets_file: str = os.getenv(
        "MOCK_TICKETS_FILE", "tests/resources/mock_tickets.json"
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
MOCK_TICKETS_FILE = settings.mock_tickets_file

OTEL_EXPORTER_OTLP_ENDPOINT = settings.OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS = settings.OTEL_EXPORTER_OTLP_HEADERS
OTEL_SERVICE_NAME = settings.OTEL_SERVICE_NAME

EVENT_BROKER_URL = settings.EVENT_BROKER_URL

VERIFY_SSL = settings.VERIFY_SSL
CLIENT_TIMEOUT_SECONDS = settings.CLIENT_TIMEOUT_SECONDS
DASH_PORT = settings.DASH_PORT
