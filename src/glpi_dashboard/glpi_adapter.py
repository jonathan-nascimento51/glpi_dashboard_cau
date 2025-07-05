"""Adapters to convert raw GLPI ticket payloads to domain objects."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .ticket_status import Impact, Priority, TicketStatus, Urgency, _BaseIntEnum

logger = logging.getLogger(__name__)


class TicketType(_BaseIntEnum):
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
    priority: Priority = Field(Priority.UNKNOWN, description="Priority")
    urgency: Urgency = Field(Urgency.UNKNOWN, description="Urgency")
    impact: Impact = Field(Impact.UNKNOWN, description="Impact")
    type: TicketType = Field(TicketType.UNKNOWN, description="Ticket type")
    date_creation: datetime | None = Field(None, description="Creation timestamp")

    model_config = ConfigDict(extra="forbid")


def _parse_int(value: Any, field: str, ticket_id: Any) -> int:
    """Coerce ``value`` to ``int`` with warning fallback.

    Args:
        value: Raw value from the payload.
        field: Name of the field being parsed.
        ticket_id: Identifier of the ticket for context in logs.

    Returns:
        Parsed integer or ``0`` if invalid.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return 0


E = TypeVar("E", bound="_BaseIntEnum")


def _parse_enum(value: Any, enum: Type[E], field: str, ticket_id: Any) -> E:
    """Convert ``value`` to ``enum`` with safe fallback.

    Args:
        value: Raw integer value.
        enum: Enumeration type to convert to.
        field: Name of the field being parsed.
        ticket_id: Identifier of the ticket for context in logs.

    Returns:
        Parsed enum member, defaulting to ``UNKNOWN`` if invalid.
    """

    if value is None:
        logger.warning("Missing %s for ticket %r", field, ticket_id)
        return enum.from_int(-1)
    try:
        return enum.from_int(int(value))
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return enum.from_int(-1)


def _parse_date(value: Any, field: str, ticket_id: Any) -> datetime | None:
    """Parse date strings into ``datetime`` objects.

    Args:
        value: Raw date string from the payload.
        field: Name of the field being parsed.
        ticket_id: Identifier of the ticket for context in logs.

    Returns:
        ``datetime`` instance or ``None`` if parsing fails.
    """

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
    """Convert a raw GLPI ticket to a domain model.

    Args:
        raw: Ticket payload as received from the API.

    Returns:
        ``CleanTicketDTO`` with validated and coerced fields.
    """

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
    priority = _parse_enum(raw.priority, Priority, "priority", ticket_id)
    urgency = _parse_enum(raw.urgency, Urgency, "urgency", ticket_id)
    impact = _parse_enum(raw.impact, Impact, "impact", ticket_id)
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
    "Priority",
    "Urgency",
    "Impact",
    "TicketType",
    "convert_ticket",
]
