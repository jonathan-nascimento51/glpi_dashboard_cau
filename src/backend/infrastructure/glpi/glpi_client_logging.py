"""Structured logger for the GLPI client using structlog."""

from __future__ import annotations

import logging

import structlog


def _configure() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


_configured = False


def get_logger(name: str) -> structlog.BoundLogger:
    global _configured
    if not _configured:
        _configure()
        _configured = True
    return structlog.get_logger(name)
