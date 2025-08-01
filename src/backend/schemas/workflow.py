from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class NextAgent(BaseModel):
    """Structured output deciding the next node."""

    next_agent: str = Field(..., description="Name of the next agent to execute")


class TicketStatus(str, Enum):
    """Allowed GLPI ticket statuses."""

    NEW = "new"
    ASSIGNED = "assigned"
    PLANNED = "planned"
    WAITING = "waiting"
    SOLVED = "solved"
    CLOSED = "closed"


class FetcherArgs(BaseModel):
    """Input parameters for the fetcher node."""

    status: TicketStatus | None = Field(
        default=None, description="Optional status filter for tickets"
    )
    limit: int = Field(..., description="Maximum number of tickets to fetch")


class Metrics(BaseModel):
    """Validated metrics produced by the analyzer."""

    total: int
    opened: int
    closed: int
