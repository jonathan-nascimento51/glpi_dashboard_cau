"""Data transfer objects and translator for GLPI tickets."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .mapping_service import MappingService

# Static mappings from numeric codes returned by the GLPI API
STATUS_MAP = {
    1: "New",
    2: "Processing (assigned)",
    3: "Processing (planned)",
    4: "Pending",
    5: "Solved",
    6: "Closed",
}

PRIORITY_MAP = {
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major",
}


class RawTicketFromAPI(BaseModel):
    """Shape of a ticket as returned by the GLPI REST API."""

    id: int
    name: str
    status: int
    priority: int
    date_creation: datetime
    users_id_assign: Optional[int] = Field(None, alias="users_id_assign")

    model_config = ConfigDict(populate_by_name=True)


class CleanTicketDTO(BaseModel):
    """Normalized ticket used internally by the application."""

    id: int
    title: str = Field(..., alias="name")
    status: str
    priority: str
    created_at: datetime = Field(..., alias="date_creation")
    assigned_to: str = "Unassigned"

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("status", mode="before")
    @classmethod
    def _validate_status(cls, v: int) -> str:  # pragma: no cover - simple mapping
        return STATUS_MAP.get(int(v), "Unknown")

    @field_validator("priority", mode="before")
    @classmethod
    def _validate_priority(cls, v: int) -> str:  # pragma: no cover - simple mapping
        return PRIORITY_MAP.get(int(v), "Unknown")


class TicketTranslator:
    """Translate raw GLPI ticket dictionaries into :class:`CleanTicketDTO`."""

    def __init__(self, mapping_service: MappingService) -> None:
        self.mapper = mapping_service

    async def translate_ticket(self, raw_ticket: Dict) -> CleanTicketDTO:
        """Validate and convert ``raw_ticket`` into :class:`CleanTicketDTO`."""

        validated_raw = RawTicketFromAPI.model_validate(raw_ticket)

        assigned_to = "Unassigned"
        if validated_raw.users_id_assign:
            assigned_to = await self.mapper.get_username(validated_raw.users_id_assign)

        clean_data = {
            "id": validated_raw.id,
            "name": validated_raw.name,
            "status": validated_raw.status,
            "priority": validated_raw.priority,
            "date_creation": validated_raw.date_creation,
            "assigned_to": assigned_to,
        }
        return CleanTicketDTO.model_validate(clean_data)
