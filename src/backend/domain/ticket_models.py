"""Data transfer models for GLPI tickets used by the Anti-Corruption Layer."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .ticket_status import Impact, Priority, TicketStatus, Urgency
from .ticket_status import _BaseIntEnum as _BaseIntEnumLocal

# Map numeric priority levels to human readable labels.
PRIORITY_LABELS = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major",
}

logger = logging.getLogger(__name__)


class TicketType(_BaseIntEnumLocal):
    """Category of ticket."""

    UNKNOWN = 0
    INCIDENT = 1
    REQUEST = 2


class RawTicketDTO(BaseModel):
    """Representation of the unprocessed GLPI ticket payload."""

    id: int | str | None = Field(None, description="Ticket identifier")
    name: str | None = Field(None, description="Short summary")
    content: str | None = Field(None, description="Detailed description")
    status: int | None = Field(None, description="Status code")
    priority: int | None = Field(None, description="Priority code")
    urgency: int | None = Field(None, description="Urgency code")
    impact: int | None = Field(None, description="Impact code")
    type: int | None = Field(None, description="Ticket type code")
    date_creation: str | None = Field(None, description="ISO date string")
    users_id_requester: int | None = Field(None, description="Requester user ID")

    model_config = ConfigDict(extra="allow")


class CleanTicketDTO(BaseModel):
    """Validated domain ticket object."""

    id: int = Field(..., description="Ticket identifier")
    title: str | None = Field(
        None,
        alias="name",
        description="Short summary",
    )
    content: str | None = Field(None, description="Detailed description")
    status: TicketStatus = Field(TicketStatus.UNKNOWN, description="Status")
    priority: Optional[str] = Field(None, description="Prioridade do ticket")
    urgency: Urgency = Field(Urgency.UNKNOWN, description="Urgency")
    impact: Impact = Field(Impact.UNKNOWN, description="Impact")
    type: TicketType = Field(TicketType.UNKNOWN, description="Ticket type")
    creation_date: datetime | None = Field(
        None, alias="date_creation", description="Creation timestamp"
    )
    requester: str | None = Field(None, description="Requester user name")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def _set_title(cls, data: dict[str, Any]) -> dict[str, Any]:
        title = data.get("title") or data.get("name")
        data["title"] = "[Título não informado]" if title in (None, "") else str(title)
        data.pop("name", None)
        return data


E = TypeVar("E", bound="_BaseIntEnumLocal")


def _parse_int(value: Any, field: str, ticket_id: Any) -> int:
    """Coerce ``value`` to ``int`` with warning fallback."""

    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return 0


def _parse_enum(value: Any, enum: Type[E], field: str, ticket_id: Any) -> E:
    """Convert ``value`` to ``enum`` with safe fallback."""

    if value is None:
        logger.warning("Missing %s for ticket %r", field, ticket_id)
        return enum.from_int(-1)
    try:
        return enum.from_int(int(value))
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return enum.from_int(-1)


def _parse_date(value: Any, field: str, ticket_id: Any) -> datetime | None:
    """Parse date strings into ``datetime`` objects."""

    if value in (None, ""):
        logger.warning("Missing %s for ticket %r", field, ticket_id)
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:  # noqa: BLE001
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return None


def _map_priority(value: Any, field: str, ticket_id: Any) -> str:
    """Map ``value`` to a priority label."""

    if value is None:
        logger.warning("Missing %s for ticket %r", field, ticket_id)
        return "Unknown"
    try:
        pid = int(value)
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return "Unknown"
    return PRIORITY_LABELS.get(pid, "Unknown")


def convert_ticket(raw: RawTicketDTO) -> CleanTicketDTO:
    """Convert a raw GLPI ticket to a domain model."""

    ticket_id = raw.id
    id_int = _parse_int(ticket_id, "id", ticket_id)

    name = raw.name
    if raw.name in (None, ""):
        logger.warning("Missing name for ticket %r", ticket_id)
        name = "[Título não informado]"
    elif type(raw.name) is not str:
        logger.warning("Invalid name=%r for ticket %r", raw.name, ticket_id)
        name = str(raw.name)

    content = None
    if raw.content is not None:
        if type(raw.content) is not str:
            logger.warning("Invalid content=%r for ticket %r", raw.content, ticket_id)
            content = str(raw.content)
        else:
            content = raw.content

    status = _parse_enum(raw.status, TicketStatus, "status", ticket_id)
    priority = _map_priority(raw.priority, "priority", ticket_id)
    urgency = _parse_enum(raw.urgency, Urgency, "urgency", ticket_id)
    impact = _parse_enum(raw.impact, Impact, "impact", ticket_id)
    ttype = _parse_enum(raw.type, TicketType, "type", ticket_id)
    date_creation = _parse_date(raw.date_creation, "date_creation", ticket_id)

    return CleanTicketDTO(
        id=id_int,
        name=name,
        content=content,
        status=status,
        priority=priority,
        urgency=urgency,
        impact=impact,
        type=ttype,
        date_creation=date_creation,
        requester=None,
    )


__all__ = [
    "RawTicketDTO",
    "CleanTicketDTO",
    "TicketStatus",
    "Priority",
    "Urgency",
    "Impact",
    "TicketType",
    "convert_ticket",
]
