"""Logging utilities with Loguru and OpenTelemetry.
Call `init_logging()` in your entrypoints before other loggers.
"""

from __future__ import annotations

import logging
import os
import sys
from contextvars import ContextVar

from loguru import logger
from opentelemetry.instrumentation.logging import LoggingInstrumentor

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class _CorrelationFilter:
    def __call__(self, record: dict) -> bool:  # pragma: no cover - simple filter
        record["extra"]["correlation_id"] = _correlation_id.get()
        return True


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - passthrough
        bound = logger.bind(correlation_id=_correlation_id.get())
        bound.opt(exception=record.exc_info).log(record.levelno, record.getMessage())


def init_logging(
    level: str | int | None = None,
    *,
    serialize: bool = True,
    enable_instrumentation: bool = True,
) -> None:
    """Initialize structured logging with Loguru.

    Parameters
    ----------
    level:
        Logging level or string (e.g. ``"INFO"``). Defaults to ``LOG_LEVEL`` env var.
    serialize:
        If ``True``, logs are emitted in JSON format.
    enable_instrumentation:
        Whether to enable OpenTelemetry logging instrumentation.

    Example
    -------
    >>> from backend.utils.logging import init_logging
    >>> init_logging("DEBUG")
    """
    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO")
        level = getattr(logging, env_level.upper(), logging.INFO)

    logger.remove()
    logger.configure(extra={"correlation_id": None})
    logger.add(
        sys.stdout,
        level=level,
        serialize=serialize,
        filter=_CorrelationFilter(),
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    logging.getLogger().setLevel(level)

    if enable_instrumentation:
        LoggingInstrumentor().instrument(set_logging_format=True)


def set_correlation_id(value: str | None) -> None:
    """Attach a correlation identifier to subsequent log records."""

    _correlation_id.set(value)


# Backwards compatibility
setup_logging = init_logging
