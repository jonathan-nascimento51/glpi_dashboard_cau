from __future__ import annotations

from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.domain.ticket_status import Impact, TicketStatus, Urgency


class TicketType(IntEnum):
    UNKNOWN = 0
    INCIDENT = 1
    REQUEST = 2


class CleanTicketDTO(BaseModel):
    """Subset of ticket fields exposed to the frontend."""

    id: int = Field(..., description="Ticket identifier")
    name: str = Field("", description="Short summary")
    content: str | None = Field(None, description="Detailed description")
    status: TicketStatus = Field(TicketStatus.UNKNOWN, description="Status")
    priority: str | None = Field(None, description="Priority")
    urgency: Urgency = Field(Urgency.UNKNOWN, description="Urgency")
    impact: Impact = Field(Impact.UNKNOWN, description="Impact")
    type: TicketType = Field(TicketType.UNKNOWN, description="Ticket type")
    date_creation: datetime | None = Field(None, description="Creation timestamp")
    requester: str | None = Field(None, description="Requester")

    model_config = ConfigDict(extra="forbid")


__all__ = ["CleanTicketDTO", "TicketType"]
