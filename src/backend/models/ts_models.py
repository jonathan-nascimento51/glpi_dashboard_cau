"""Pydantic models for the tickets summary endpoint."""

from __future__ import annotations

from typing import Dict

from pydantic import RootModel


class TicketsSummaryPerLevel(RootModel[Dict[str, Dict[str, int]]]):
    """Model representing the ticket status summary per service level."""
