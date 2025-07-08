"""Convenience wrapper for the worker API entrypoint.

All imports use the installed ``glpi_dashboard`` package instead of the
former ``src.glpi_dashboard`` path.
"""

import logging
import os

from glpi_dashboard.config.settings import KNOWLEDGE_BASE_FILE
from glpi_dashboard.logging_config import init_logging
from glpi_dashboard.services.glpi_session import GLPISession
from glpi_dashboard.services.worker_api import (
    create_app,
)
from glpi_dashboard.services.worker_api import main as _main
from glpi_dashboard.services.worker_api import (
    redis_client,
)

__all__ = ["create_app", "redis_client", "GLPISession", "main"]


def main() -> None:
    init_logging(os.getenv("LOG_LEVEL"))
    logging.getLogger(__name__).info("Knowledge base file: %s", KNOWLEDGE_BASE_FILE)
    _main()


if __name__ == "__main__":
    main()
