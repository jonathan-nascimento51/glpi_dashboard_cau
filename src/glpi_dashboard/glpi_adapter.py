"""Adapters to convert raw GLPI ticket payloads to domain objects."""

from __future__ import annotations

import logging
from datetime import datetime
from enum import IntEnum
from typing import Any, Type, TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class _SafeIntEnum(IntEnum):
    """Base enum that falls back to ``UNKNOWN`` for unexpected values."""

    @classmethod
    def _missing_(cls, value: Any) -> "_SafeIntEnum":
        logger.warning("Unknown %s value: %r", cls.__name__, value)
        return cls.__members__.get("UNKNOWN")  # type: ignore[return-value]


class TicketStatus(_SafeIntEnum):
    """Possible ticket statuses in GLPI."""

    UNKNOWN = 0
    NEW = 1
    ASSIGNED = 2
    PLANNED = 3
    PENDING = 4
    SOLVED = 5
    CLOSED = 6


class PriorityLevel(_SafeIntEnum):
    """Priority level for tickets."""

    UNKNOWN = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6


class UrgencyLevel(_SafeIntEnum):
    """Urgency level for tickets."""

    UNKNOWN = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6


class ImpactLevel(_SafeIntEnum):
    """Impact level for tickets."""

    UNKNOWN = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6


class TicketType(_SafeIntEnum):
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

    model_config = ConfigDict(extra="allow")


class CleanTicketDTO(BaseModel):
    """Validated domain ticket object."""

    id: int = Field(..., description="Ticket identifier")
    name: str = Field("", description="Short summary")
    content: str | None = Field(None, description="Detailed description")
    status: TicketStatus = Field(TicketStatus.UNKNOWN, description="Status")
    priority: PriorityLevel = Field(PriorityLevel.UNKNOWN, description="Priority")
    urgency: UrgencyLevel = Field(UrgencyLevel.UNKNOWN, description="Urgency")
    impact: ImpactLevel = Field(ImpactLevel.UNKNOWN, description="Impact")
    type: TicketType = Field(TicketType.UNKNOWN, description="Ticket type")
    date_creation: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(extra="forbid")


def _parse_int(value: Any, field: str, ticket_id: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return 0


E = TypeVar("E", bound="_SafeIntEnum")


def _parse_enum(value: Any, enum: Type[E], field: str, ticket_id: Any) -> E:
    unknown = cast(E, enum.__members__.get("UNKNOWN"))
    if value is None:
        logger.warning("Missing %s for ticket %r", field, ticket_id)
        return unknown
    try:
        return enum(int(value))
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return unknown


def _parse_date(value: Any, field: str, ticket_id: Any) -> datetime | None:
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


def convert_ticket(raw: RawTicketDTO) -> CleanTicketDTO:
    """Convert a raw GLPI ticket to a domain model."""

    ticket_id = raw.id
    id_int = _parse_int(ticket_id, "id", ticket_id)

    name = raw.name or ""
    if raw.name is None:
        logger.warning("Missing name for ticket %r", ticket_id)
    elif not isinstance(raw.name, str):
        logger.warning("Invalid name=%r for ticket %r", raw.name, ticket_id)
        name = str(raw.name)

    content = None
    if raw.content is not None:
        if not isinstance(raw.content, str):
            logger.warning("Invalid content=%r for ticket %r", raw.content, ticket_id)
            content = str(raw.content)
        else:
            content = raw.content

    status = _parse_enum(raw.status, TicketStatus, "status", ticket_id)
    priority = _parse_enum(raw.priority, PriorityLevel, "priority", ticket_id)
    urgency = _parse_enum(raw.urgency, UrgencyLevel, "urgency", ticket_id)
    impact = _parse_enum(raw.impact, ImpactLevel, "impact", ticket_id)
    ttype = _parse_enum(raw.type, TicketType, "type", ticket_id)
    created = _parse_date(raw.date_creation, "date_creation", ticket_id)

    return CleanTicketDTO(
        id=id_int,
        name=name,
        content=content,
        status=status,
        priority=priority,
        urgency=urgency,
        impact=impact,
        type=ttype,
        date_creation=created,
    )


__all__ = [
    "RawTicketDTO",
    "CleanTicketDTO",
    "TicketStatus",
    "PriorityLevel",
    "UrgencyLevel",
    "ImpactLevel",
    "TicketType",
    "convert_ticket",
]
