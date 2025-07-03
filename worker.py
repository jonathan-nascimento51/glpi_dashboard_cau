"""Convenience wrapper for the worker API entrypoint.

All imports use the installed ``glpi_dashboard`` package instead of the
former ``src.glpi_dashboard`` path.
"""

from glpi_dashboard.services.worker_api import (
    create_app,
    main as _main,
    redis_client,
)
from glpi_dashboard.services.glpi_api_client import GlpiApiClient
from glpi_dashboard.logging_config import setup_logging

__all__ = ["create_app", "redis_client", "GlpiApiClient", "main"]


def main() -> None:
    setup_logging()
    _main()


if __name__ == "__main__":
    main()
