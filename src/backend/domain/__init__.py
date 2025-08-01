"""Domain layer package."""

# Importações locais para evitar circular import
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

# Importações de ticket_models movidas para dentro de funções quando necessário
# Exemplo:
# def get_clean_ticket_dto():
#     from backend.schemas.ticket_models import CleanTicketDTO
#     return CleanTicketDTO

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
