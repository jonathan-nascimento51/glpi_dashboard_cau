"""Structured logging helpers for the GLPI sync client."""

from __future__ import annotations

import logging
import threading
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars

_configure_lock = threading.Lock()
_configured = False


def _configure(level: int = logging.INFO) -> None:
    """Configure structlog for JSON output with context variable support."""

    logging.basicConfig(level=level, format="%(message)s")
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def init_logging(level: int = logging.INFO) -> None:
    """Initialize structlog configuration once."""

    global _configured
    if _configured:
        return
    with _configure_lock:
        if not _configured:
            _configure(level)
            _configured = True


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a structured logger without configuring logging."""

    return structlog.get_logger(name)


def setup_logger(name: str, *, level: int = logging.INFO) -> structlog.BoundLogger:
    """Initialize logging and return a logger instance."""

    init_logging(level)
    return get_logger(name)


def bind_request(**values: Any) -> None:
    """Attach request specific context to subsequent log records."""

    bind_contextvars(**values)


def clear_request() -> None:
    """Remove any previously bound request context."""

    clear_contextvars()


__all__ = [
    "get_logger",
    "init_logging",
    "bind_request",
    "clear_request",
    "setup_logger",
]
