import logging
from enum import Enum
from typing import Dict, Optional, Type

import aiohttp

logger = logging.getLogger(__name__)


class GlpiHttpError(Enum):
    """
    Enum mapping common GLPI API HTTP status codes to their meanings.
    """

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500

    def __str__(self) -> str:
        """
        Returns a human-readable string for the error, e.g., "400 Bad Request".
        """
        return f"{self.value} {self.name.replace('_', ' ').title()}"


class GLPIAPIError(Exception):
    """
    Base exception for all GLPI API errors.

    Attributes:
        status_code: The HTTP status code of the error.
        message: A descriptive error message.
        response_data: Optional dictionary containing the raw
            response data from the API.
    """

    def __init__(
        self, status_code: int, message: str, response_data: Optional[dict] = None
    ):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"GLPI API Error {status_code}: {message}")


class GLPIBadRequestError(GLPIAPIError):
    """400 Bad Request: The request was malformed or missing required fields."""

    pass


class GLPIUnauthorizedError(GLPIAPIError):
    """401 Unauthorized: Invalid or missing API key/token."""

    pass


class GLPIForbiddenError(GLPIAPIError):
    """403 Forbidden: User or function without permission for the action."""

    pass


class GLPINotFoundError(GLPIAPIError):
    """404 Not Found: The requested resource does not exist or URL is incorrect."""

    pass


class GLPITooManyRequestsError(GLPIAPIError):
    """429 Too Many Requests: Rate limit of requests exceeded."""

    pass


class GLPIInternalServerError(GLPIAPIError):
    """500 Internal Server Error: An internal error occurred on the GLPI server."""

    pass


# Mapping HTTP status codes to custom exception classes
HTTP_STATUS_ERROR_MAP: Dict[int, Type[GLPIAPIError]] = {
    GlpiHttpError.BAD_REQUEST.value: GLPIBadRequestError,
    GlpiHttpError.UNAUTHORIZED.value: GLPIUnauthorizedError,
    GlpiHttpError.FORBIDDEN.value: GLPIForbiddenError,
    GlpiHttpError.NOT_FOUND.value: GLPINotFoundError,
    GlpiHttpError.TOO_MANY_REQUESTS.value: GLPITooManyRequestsError,
    GlpiHttpError.INTERNAL_SERVER_ERROR.value: GLPIInternalServerError,
}


def parse_error(response: aiohttp.ClientResponse, data: Optional[dict] = None) -> str:
    """Return a readable error message from a response and optional payload."""
    if data and isinstance(data, dict) and "error" in data:
        return data.get("error", "")
    try:
        status_text = response.reason or "Unknown Error"
        return f"HTTP {response.status}: {status_text}"
    except Exception as e:
        logger.error(f"Error parsing response for human-readable message: {e}")
        return (
            "An unexpected error occurred while processing the API response"
            f" (Status: {response.status})."
        )
