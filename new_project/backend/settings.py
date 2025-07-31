from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Minimal settings for the experimental backend."""

    GLPI_BASE_URL: str = "http://localhost/apirest.php"
    GLPI_APP_TOKEN: str = "dummy_app_token"
    GLPI_USERNAME: str = "glpi"
    GLPI_PASSWORD: str = "glpi"
    GLPI_USER_TOKEN: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

GLPI_BASE_URL = settings.GLPI_BASE_URL
GLPI_APP_TOKEN = settings.GLPI_APP_TOKEN
GLPI_USERNAME = settings.GLPI_USERNAME
GLPI_PASSWORD = settings.GLPI_PASSWORD
GLPI_USER_TOKEN = settings.GLPI_USER_TOKEN
