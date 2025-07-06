"""Anti-Corruption Layer for the GLPI dashboard."""

from .normalization import FIELD_ALIASES, REQUIRED_FIELDS, process_raw
from .ticket_models import (
    CleanTicketDTO,
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
]
