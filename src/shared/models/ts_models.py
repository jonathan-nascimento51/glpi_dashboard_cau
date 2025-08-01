from __future__ import annotations

from enum import IntEnum

from shared.dto import CleanTicketDTO


class TicketType(IntEnum):
    UNKNOWN = 0
    INCIDENT = 1
    REQUEST = 2


__all__ = ["CleanTicketDTO", "TicketType"]
