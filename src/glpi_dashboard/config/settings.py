import os
from dotenv import load_dotenv

load_dotenv()

# GLPI API Configuration
GLPI_BASE_URL = os.getenv("GLPI_BASE_URL", "http://localhost/glpi/apirest.php")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN", "your_app_token")
GLPI_USERNAME = os.getenv("GLPI_USERNAME", "glpi_user")
GLPI_PASSWORD = os.getenv("GLPI_PASSWORD", "glpi_password")
GLPI_USER_TOKEN = os.getenv(
    "GLPI_USER_TOKEN", None
)  # Optional, if using user token auth

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "glpi_dashboard")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_TTL_SECONDS = int(
    os.getenv("REDIS_TTL_SECONDS", "3600")
)  # 1 hour TTL for raw JSON

# Pipeline Configuration
FETCH_PAGE_SIZE = int(os.getenv("FETCH_PAGE_SIZE", "50"))  # Default range 0-50
MV_REFRESH_INTERVAL_MINUTES = int(
    os.getenv("MV_REFRESH_INTERVAL_MINUTES", "5")
)

# All operations run online against the GLPI API
