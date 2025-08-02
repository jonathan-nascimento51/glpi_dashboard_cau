from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# Importações do domínio feitas localmente para evitar circular import
def get_domain_enums():
    from backend.domain.ticket_status import (
        Impact,
        TicketStatus,
        Urgency,
    )
    from backend.domain.ticket_status import (
        _BaseIntEnum as _BaseIntEnumLocal,
    )

    return Impact, TicketStatus, Urgency, _BaseIntEnumLocal


# Set up logger
logger = logging.getLogger(__name__)

# Map numeric priority levels to human readable labels.
PRIORITY_LABELS = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major",
}


class TicketType:
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


STATUS_MAP = {
    1: "New",
    2: "Processing (assigned)",
    3: "Processing (planned)",
    4: "Pending",
    5: "Solved",
    6: "Closed",
}

TEXT_STATUS_MAP = {label.lower(): label for label in STATUS_MAP.values()}

PRIORITY_MAP_PT = {
    1: "Muito Baixa",
    2: "Baixa",
    3: "Média",
    4: "Alta",
    5: "Muito Alta",
    6: "Maior",
}

DEFAULT_TITLE = "[Título não informado]"


class CleanTicketDTO(BaseModel):
    """Normalized ticket used internally by the application."""

    id: int
    title: Optional[str] = Field(default=None, alias="name")
    status: str
    priority: Optional[str] = Field(
        None, description="Priority as a human-readable label"
    )
    created_at: Optional[datetime] = Field(default=None, alias="date_creation")
    assigned_to: str = "Unassigned"
    requester: Optional[str] = None
    group: str | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _sanitize_title(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        title = data.get("name")
        if "name" not in data or title == "" or title is None:
            data["name"] = DEFAULT_TITLE
        else:
            data["name"] = str(title)
        return data

    @field_validator("status", mode="before")
    @classmethod
    def _validate_status(cls, v: int | str) -> str:
        if isinstance(v, str):
            value = v.strip()
            if value.isdigit():
                v = int(value)
            else:
                return TEXT_STATUS_MAP.get(value.lower(), "Unknown")
        return STATUS_MAP.get(int(v), "Unknown") if str(v).isdigit() else "Unknown"

    @field_validator("priority", mode="before")
    @classmethod
    def _validate_priority(cls, v: int | str | None) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str) and not v.isdigit():
            return v
        if isinstance(v, int):
            return PRIORITY_MAP_PT.get(v, PRIORITY_LABELS.get(v, "Unknown"))
        if str(v).isdigit():
            num = int(v)
            return PRIORITY_MAP_PT.get(num, PRIORITY_LABELS.get(num, "Unknown"))
        return "Unknown"


E = TypeVar("E")


def _parse_int(value: Any, field: str, ticket_id: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return 0


def _parse_enum(value: Any, enum: Type[E], field: str, ticket_id: Any) -> E:
    if value is None:
        logger.warning("Missing %s for ticket %r", field, ticket_id)
        # Garante que retorna um valor do tipo E (enum.UNKNOWN)
        return enum.UNKNOWN  # type: ignore
    try:
        # Garante que enum é chamado corretamente
        return enum(int(value))  # type: ignore
    except (TypeError, ValueError):
        logger.warning("Invalid %s=%r for ticket %r", field, value, ticket_id)
        return enum.UNKNOWN  # type: ignore


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


def _map_priority(value: Any, field: str, ticket_id: Any) -> str:
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
    Impact, TicketStatus, Urgency, _BaseIntEnumLocal = get_domain_enums()
    ticket_id = raw.id
    id_int = _parse_int(ticket_id, "id", ticket_id)

    name = raw.name
    if raw.name in (None, ""):
        logger.warning("Missing name for ticket %r", ticket_id)
        name = DEFAULT_TITLE
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

    if status != TicketStatus.NEW:
        raise ValueError("Ticket is not NEW")

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
    "TicketType",
    "convert_ticket",
]
