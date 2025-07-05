"""Convenience wrapper for the worker API entrypoint.

All imports use the installed ``glpi_dashboard`` package instead of the
former ``src.glpi_dashboard`` path.
"""

import os

from glpi_dashboard.logging_config import init_logging
from glpi_dashboard.services.glpi_api_client import GlpiApiClient
from glpi_dashboard.services.worker_api import (
    create_app,
)
from glpi_dashboard.services.worker_api import main as _main
from glpi_dashboard.services.worker_api import (
    redis_client,
)

__all__ = ["create_app", "redis_client", "GlpiApiClient", "main"]


def main() -> None:
    init_logging(os.getenv("LOG_LEVEL"))
    _main()


if __name__ == "__main__":
    main()
