"""Backend-specific utilities and compatibility exports."""

from shared.utils.logging import init_logging, set_correlation_id

from .pagination import paginate_items

__all__ = [
    "init_logging",
    "set_correlation_id",
    "paginate_items",
]
