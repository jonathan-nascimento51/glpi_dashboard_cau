from __future__ import annotations

import logging
from enum import IntEnum
from typing import Type, TypeVar

logger = logging.getLogger(__name__)

E = TypeVar("E", bound="_BaseIntEnum")


class _BaseIntEnum(IntEnum):
    """IntEnum with a safe ``from_int`` constructor."""

    @classmethod
    def from_int(cls: Type[E], value: int) -> E:
        """Return enum value or ``UNKNOWN`` if ``value`` is invalid."""
        try:
            return cls(value)
        except ValueError:
            logger.warning("Unknown %s value: %r", cls.__name__, value)
            return cls.__members__["UNKNOWN"]


class TicketStatus(_BaseIntEnum):
    """GLPI ticket statuses."""

    UNKNOWN = 0
    NEW = 1
    ASSIGNED = 2
    PLANNED = 3
    PENDING = 4
    SOLVED = 5
    CLOSED = 6


class Priority(_BaseIntEnum):
    """Ticket priority levels."""

    UNKNOWN = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6


class Urgency(_BaseIntEnum):
    """Ticket urgency levels."""

    UNKNOWN = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6


class Impact(_BaseIntEnum):
    """Ticket impact levels."""

    UNKNOWN = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    MAJOR = 6


__all__ = [
    "TicketStatus",
    "Priority",
    "Urgency",
    "Impact",
]
