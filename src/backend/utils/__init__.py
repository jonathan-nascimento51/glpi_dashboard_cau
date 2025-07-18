"""Backend-specific utilities and compatibility exports."""

from shared.utils.logging import init_logging, set_correlation_id

from .pagination import paginate_items
from .pipeline import process_raw, save_json

__all__ = [
    "process_raw",
    "save_json",
    "init_logging",
    "set_correlation_id",
    "paginate_items",
]
