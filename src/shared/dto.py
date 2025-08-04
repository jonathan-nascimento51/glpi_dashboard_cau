"""Data transfer objects and translator for GLPI tickets."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.ticket_models import CleanTicketDTO

if TYPE_CHECKING:  # Avoid runtime import cycle
    from backend.adapters.mapping_service import MappingService

# Static mappings from numeric codes returned by the GLPI API
STATUS_MAP = {
    1: "new",
    2: "processing (assigned)",
    3: "processing (planned)",
    4: "pending",
    5: "solved",
    6: "closed",
}

# Map textual statuses (e.g., "closed") to the same canonical labels
TEXT_STATUS_MAP = {label: label for label in STATUS_MAP.values()}

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
