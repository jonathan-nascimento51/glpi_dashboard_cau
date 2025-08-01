"""Domain layer package."""

from backend.schemas.ticket_models import (
    CleanTicketDTO,
    RawTicketDTO,
    TicketType,
    convert_ticket,
)

from .exceptions import (
    HTTP_STATUS_ERROR_MAP,
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GlpiHttpError,
    GLPIInternalServerError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIUnauthorizedError,
    parse_error,
)
from .ticket_status import Impact, Priority, TicketStatus, Urgency
from .tool_error import ToolError

__all__ = [
    "TicketStatus",
    "Priority",
    "Urgency",
    "Impact",
    "TicketType",
    "RawTicketDTO",
    "CleanTicketDTO",
    "convert_ticket",
    "GLPIAPIError",
    "GLPIBadRequestError",
    "GLPIUnauthorizedError",
    "GLPIForbiddenError",
    "GLPINotFoundError",
    "GLPITooManyRequestsError",
    "GLPIInternalServerError",
    "GlpiHttpError",
    "HTTP_STATUS_ERROR_MAP",
    "parse_error",
    "ToolError",
]
