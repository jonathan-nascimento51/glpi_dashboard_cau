import asyncio
import random
import time
from enum import Enum
from functools import wraps
from typing import Callable, Any, Dict, Optional, Type, Union
import logging

import aiohttp

# Configure minimal logging for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        response_data: Optional dictionary containing the raw response data from the API.
    """
    def __init__(self, status_code: int, message: str, response_data: Optional[dict] = None):
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

def parse_error(response: aiohttp.ClientResponse) -> str:
    """
    Parses an aiohttp ClientResponse to return a human-readable error message.
    This function is synchronous and relies on information directly available from the response object.

    Args:
        response: The aiohttp.ClientResponse object.

    Returns:
        A human-readable error message based on the HTTP status and reason.
    """
    try:
        status_text = response.reason if response.reason else "Unknown Error"
        return f"HTTP {response.status}: {status_text}"
    except Exception as e:
        logger.error(f"Error parsing response for human-readable message: {e}")
        return f"An unexpected error occurred while processing the API response (Status: {response.status})."

def glpi_retry(
    max_retries: int = 5,
    base_delay: float = 0.1, # seconds
    retry_on_status: tuple[int,...] = (
        GlpiHttpError.TOO_MANY_REQUESTS.value,
        GlpiHttpError.INTERNAL_SERVER_ERROR.value
    )
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator for asynchronous GLPI API calls that implements jittered exponential back-off.

    Retries on specified HTTP status codes (default: 429, 500) and network errors.
    Translates other HTTP error codes into custom GLPIAPIError exceptions.

    Args:
        max_retries: Maximum number of retry attempts (default: 5).
        base_delay: Base delay in seconds for exponential back-off (default: 0.1).
        retry_on_status: Tuple of HTTP status codes on which to retry.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except GLPIAPIError as e:
                    # Check if the raised GLPIAPIError is retryable
                    if e.status in retry_on_status and attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        jitter = random.uniform(0, delay)
                        sleep_time = delay + jitter
                        logger.warning(
                            f"API call failed with status {e.status} ({e.message}). "
                            f"Retrying in {sleep_time:.2f} seconds (attempt {attempt + 1}/{max_retries})."
                        )
                        await asyncio.sleep(sleep_time)
                    else:
                        # Re-raise if not a retryable status or max retries exceeded
                        raise
                except aiohttp.ClientError as e:
                    # Catch network-level errors (e.g., connection lost)
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        jitter = random.uniform(0, delay)
                        sleep_time = delay + jitter
                        logger.warning(
                            f"Network error during API call: {e}. "
                            f"Retrying in {sleep_time:.2f} seconds (attempt {attempt + 1}/{max_retries})."
                        )
                        await asyncio.sleep(sleep_time)
                    else:
                        # Raise a generic GLPIAPIError for persistent network issues
                        raise GLPIAPIError(0, f"Network error after {max_retries} retries: {e}")
                except Exception as e:
                    # Catch any other unexpected exceptions and wrap them in GLPIAPIError
                    raise GLPIAPIError(0, f"An unexpected error occurred: {e}")
            
            # This line should ideally not be reached if max_retries is handled correctly
            raise GLPIAPIError(0, f"API call failed after {max_retries} retries.")
        return wrapper
    return decorator