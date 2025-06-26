"""Service layer exports for the GLPI dashboard."""

from .glpi_session import Credentials, GLPISession
from .exceptions import (
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIUnauthorizedError,
    GLPIForbiddenError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIInternalServerError,
    HTTP_STATUS_ERROR_MAP,
    glpi_retry,
    parse_error,
)

__all__ = [
    "Credentials",
    "GLPISession",
    "GLPIAPIError",
    "GLPIBadRequestError",
    "GLPIUnauthorizedError",
    "GLPIForbiddenError",
    "GLPINotFoundError",
    "GLPITooManyRequestsError",
    "GLPIInternalServerError",
    "HTTP_STATUS_ERROR_MAP",
    "glpi_retry",
    "parse_error",
]