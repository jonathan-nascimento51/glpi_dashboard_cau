"""Compatibility layer for the ticket summary read model."""

import importlib

from backend.db.read_model import (
    TicketSummary,
    get_ticket_summary,
    refresh_read_model,
)

ticket_summary = importlib.import_module("backend.db.read_model")

__all__ = [
    "TicketSummary",
    "get_ticket_summary",
    "refresh_read_model",
    "ticket_summary",
]
