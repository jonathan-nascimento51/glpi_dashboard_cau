"""Anti-Corruption Layer for the GLPI dashboard."""

from .dto import CleanTicketDTO, TicketTranslator
from .mapping_service import MappingService
from .normalization import FIELD_ALIASES, REQUIRED_FIELDS, process_raw
from .ticket_models import (
    Impact,
    Priority,
    RawTicketDTO,
    TicketStatus,
    TicketType,
    Urgency,
    convert_ticket,
)

__all__ = [
    "RawTicketDTO",
    "CleanTicketDTO",
    "TicketType",
    "convert_ticket",
    "TicketStatus",
    "Priority",
    "Urgency",
    "Impact",
    "process_raw",
    "FIELD_ALIASES",
    "REQUIRED_FIELDS",
    "MappingService",
    "TicketTranslator",
]
