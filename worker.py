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

from shared.utils.logging import init_logging
from src.backend.api.worker_api import (
    create_app,
)
from src.backend.api.worker_api import main as _main
from src.backend.api.worker_api import (
    redis_client,
)
from src.backend.core.settings import KNOWLEDGE_BASE_FILE
from src.backend.infrastructure.glpi.glpi_session import GLPISession

# Initialize logging as early as possible
init_logging(level=os.getenv("LOG_LEVEL", "INFO"))

__all__ = ["create_app", "redis_client", "GLPISession", "main"]


def main() -> None:
    logger = logging.getLogger(__name__)
    logger.info("Knowledge base file: %s", KNOWLEDGE_BASE_FILE)
    _main()


if __name__ == "__main__":
    main()
