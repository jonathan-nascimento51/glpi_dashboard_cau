"""Convenience wrapper for the worker API entrypoint."""

from src.glpi_dashboard.services.worker import (
    create_app,
    main as _main,
    redis_client,
)
from src.glpi_dashboard.services.worker import GLPISession

__all__ = ["create_app", "redis_client", "GLPISession", "main"]


def main() -> None:
    _main()


if __name__ == "__main__":
    main()
