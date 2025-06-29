"""Convenience wrapper for the worker API entrypoint."""

from src.glpi_dashboard.services.worker_api import (
    create_app,
    main as _main,
    redis_client,
)
from src.glpi_dashboard.services.worker_api import GLPISession
from src.glpi_dashboard.logging_config import setup_logging

__all__ = ["create_app", "redis_client", "GLPISession", "main"]


def main() -> None:
    setup_logging()
    _main()


if __name__ == "__main__":
    main()
