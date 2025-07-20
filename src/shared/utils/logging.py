"""Logging utilities with Loguru and OpenTelemetry.
Call `init_logging()` in your entrypoints before other loggers.
"""

from __future__ import annotations

import logging
import os
import sys
from contextvars import ContextVar
from typing import Any

from loguru import logger
from opentelemetry.instrumentation.logging import LoggingInstrumentor

_is_initialized: bool = False
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
    serialize: bool | None = None,
    enable_instrumentation: bool = True,
) -> None:
    """Initialize structured logging with Loguru.

    Parameters
    ----------
    level:
        Logging level or string (e.g. ``"INFO"``). Defaults to ``LOG_LEVEL`` env var.
    serialize:
        If ``True``, logs are emitted in JSON format. Defaults to ``True`` unless the
        ``LOG_FORMAT`` environment variable is set to ``"text"``.
    enable_instrumentation:
        Whether to enable OpenTelemetry logging instrumentation.

    Example
    -------
    >>> from shared.utils.logging import init_logging
    >>> init_logging("DEBUG")
    """
    global _is_initialized
    if _is_initialized:
        return

    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO")
        level = getattr(logging, env_level.upper(), logging.INFO)

    # Determine environment and output format
    env = os.getenv("APP_ENV", "development").lower()
    is_production = env == "production"

    if serialize is None and is_production or serialize is not None and is_production:
        serialize = True
    elif serialize is None:
        serialize = os.getenv("LOG_FORMAT", "json").lower() != "text"
    # Enable verbose diagnostics only if LOG_DEBUG is set and not in production
    debug_mode = os.getenv("LOG_DEBUG", "false").lower() in ("true", "1", "t")
    if is_production:
        debug_mode = False

    logger.remove()
    logger.configure(extra={"correlation_id": None})
    logger.add(
        sys.stdout,
        level=(
            level if level is not None else "INFO"
        ),  # Default to "INFO" if level is None
        serialize=serialize,
        colorize=not serialize,
        filter=_CorrelationFilter(),  # type: ignore[arg-type]
        enqueue=True,
        backtrace=debug_mode,
        diagnose=debug_mode,
    )

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    logging.getLogger().setLevel(level if level is not None else logging.INFO)

    if enable_instrumentation:
        LoggingInstrumentor().instrument(set_logging_format=True)

    _is_initialized = True


def get_logger(name: str | None = None) -> Any:
    """Return a logger bound with the given name."""

    return logger.bind(module=name) if name else logger


def set_correlation_id(value: str | None) -> None:
    """Attach a correlation identifier to subsequent log records."""

    _correlation_id.set(value)


# Backwards compatibility for legacy modules (log_config.py, logging_config.py)
setup_logging = init_logging
