"""Convenience wrapper for the worker API entrypoint.

All imports now reference ``src.backend`` explicitly to avoid
confusion with the Docker build context.
"""

import contextlib
import logging
import os

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv

    # Load environment variables from .env file for local development
    load_dotenv()

from backend.api.worker_api import (
    create_app,
    redis_client,
)
from backend.api.worker_api import main as _main
from backend.core.settings import KNOWLEDGE_BASE_FILE
from backend.infrastructure.glpi import glpi_client_logging
from backend.infrastructure.glpi.glpi_session import GLPISession
from shared.utils.logging import init_logging
from shared.utils.security import validate_glpi_tokens

# Initialize structured logging as early as possible
log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_name.upper(), logging.INFO)
init_logging(log_level)
glpi_client_logging.init_logging(log_level)

__all__ = ["create_app", "redis_client", "GLPISession", "main"]


def main() -> None:
    logger = logging.getLogger(__name__)
    validate_glpi_tokens()
    logger.info("Knowledge base file: %s", KNOWLEDGE_BASE_FILE)
    _main()


if __name__ == "__main__":
    main()
