"""Convenience wrapper for the worker API entrypoint.

All imports now reference ``src.backend`` explicitly to avoid
confusion with the Docker build context.
"""

import logging
import os

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

__all__ = ["create_app", "redis_client", "GLPISession", "main"]


def main() -> None:
    init_logging(os.getenv("LOG_LEVEL"))
    logging.getLogger(__name__).info("Knowledge base file: %s", KNOWLEDGE_BASE_FILE)
    _main()


if __name__ == "__main__":
    main()
