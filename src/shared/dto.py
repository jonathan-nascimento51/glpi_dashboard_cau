"""Data transfer objects and translator for GLPI tickets."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

try:  # Avoid runtime import cycle during initialization
    from backend.adapters.mapping_service import MISSING_PRIORITY
except Exception:  # pragma: no cover - fallback if import fails
    MISSING_PRIORITY = -1

if TYPE_CHECKING:  # Avoid runtime import cycle
    from backend.adapters.mapping_service import MappingService

# Static mappings from numeric codes returned by the GLPI API
STATUS_MAP = {
    1: "New",
    2: "Processing (assigned)",
    3: "Processing (planned)",
    4: "Pending",
    5: "Solved",
    6: "Closed",
}

# Map textual statuses (e.g., "closed") to the same canonical labels
TEXT_STATUS_MAP = {label.lower(): label for label in STATUS_MAP.values()}

# Priority labels in English (legacy) and Portuguese used in the dashboard.
PRIORITY_MAP = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major",
}

PRIORITY_MAP_PT = {
    1: "Muito Baixa",
    2: "Baixa",
    3: "Média",
    4: "Alta",
    5: "Muito Alta",
    6: "Maior",
}

# Fallback title assigned when a ticket comes with an empty or null name
DEFAULT_TITLE = "[Título não informado]"


class RawTicketFromAPI(BaseModel):
    """Shape of a ticket as returned by the GLPI REST API."""

    id: int
    name: Optional[str] = Field(default=None)
    status: Union[int, str]
    priority: Optional[int] = Field(
        None, description="Priority as a numeric value from GLPI"
    )
    date_creation: Optional[datetime] = Field(default=None)
    users_id_assign: Optional[int] = Field(None, alias="users_id_assign")
    users_id_requester: Optional[int] = Field(None, alias="users_id_requester")

    model_config = ConfigDict(populate_by_name=True)


class CleanTicketDTO(BaseModel):
    """Normalized ticket used internally by the application."""

    id: int
    title: Optional[str] = Field(
        default=None,
        alias="name",
    )
    status: str
    priority: Optional[str] = Field(
        None, description="Priority as a human-readable label"
    )
    created_at: Optional[datetime] = Field(default=None, alias="date_creation")
    assigned_to: str = "Unassigned"
    requester: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

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
        """Normalize integer or textual status values to labels."""

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
            return PRIORITY_MAP_PT.get(v, PRIORITY_MAP.get(v, "Unknown"))
        if str(v).isdigit():
            num = int(v)
            return PRIORITY_MAP_PT.get(num, PRIORITY_MAP.get(num, "Unknown"))
        return "Unknown"


class TicketTranslator:
    """Translate raw GLPI ticket dictionaries into :class:`CleanTicketDTO`."""

    def __init__(self, mapping_service: "MappingService") -> None:
        self.mapper = mapping_service

    async def translate_ticket(self, raw_ticket: Dict[str, Any]) -> CleanTicketDTO:
        """Validate and convert ``raw_ticket`` into :class:`CleanTicketDTO`."""

        validated_raw = RawTicketFromAPI.model_validate(raw_ticket)

        assigned_to = "Unassigned"
        if validated_raw.users_id_assign:
            assigned_to = await self.mapper.get_username(validated_raw.users_id_assign)

        requester = None
        if validated_raw.users_id_requester:
            requester = await self.mapper.get_username(validated_raw.users_id_requester)

        if validated_raw.priority is not None:
            priority_label = self.mapper.priority_label(validated_raw.priority)
        else:
            priority_label = "Unknown"

        clean_data: Dict[str, Any] = {
            "id": validated_raw.id,
            "name": validated_raw.name,
            "status": validated_raw.status,
            "priority": priority_label,
            "date_creation": validated_raw.date_creation,
            "assigned_to": assigned_to,
            "requester": requester,
        }
        return CleanTicketDTO.model_validate(clean_data)
