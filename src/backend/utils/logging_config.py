from __future__ import annotations

import logging
import os
import sys
from contextvars import ContextVar

from loguru import logger

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class _CorrelationFilter:
    def __call__(self, record: dict) -> bool:  # pragma: no cover - simple filter
        record["extra"]["correlation_id"] = _correlation_id.get()
        return True


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - passthrough
        bound = logger.bind(correlation_id=_correlation_id.get())
        bound.opt(exception=record.exc_info).log(record.levelno, record.getMessage())


def init_logging(level: str | int | None = None) -> None:
    """Initialize JSON logging with Loguru."""

    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO")
        level = getattr(logging, env_level.upper(), logging.INFO)

    logger.remove()
    logger.configure(extra={"correlation_id": None})
    logger.add(sys.stdout, level=level, serialize=True, filter=_CorrelationFilter())

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    logging.getLogger().setLevel(level)


def set_correlation_id(value: str | None) -> None:
    """Attach a correlation identifier to subsequent log records."""

    _correlation_id.set(value)


# Backwards compatibility
setup_logging = init_logging
