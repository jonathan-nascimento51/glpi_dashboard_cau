import logging
import time
from threading import Lock
from typing import Any, Dict, Optional

import requests

__all__ = [
    "GLPIAuthError",
    "GLPIPermissionError",
    "GLPIRetryError",
    "http_request_with_retry",
]


logger = logging.getLogger(__name__)


class GLPIAuthError(Exception):
    """Raised when authentication fails even after refresh."""


class GLPIPermissionError(Exception):
    """Raised when the user lacks permission for the requested resource."""


class GLPIRetryError(Exception):
    """Raised when a request keeps failing after retries."""


_refresh_lock = Lock()


def http_request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    auth_client: Optional[Any] = None,
    max_attempts: int = 3,
    **kwargs: Any,
) -> requests.Response:
    """Perform an HTTP request with retry and GLPI specific error handling."""

    attempt = 1
    wait_seconds = 1
    headers = headers or {}

    while attempt <= max_attempts:
        try:
            resp = session.request(method, url, headers=headers, **kwargs)
        except requests.RequestException as exc:
            if attempt >= max_attempts:
                logger.error("GLPI API network error: %s", exc)
                raise GLPIRetryError(str(exc)) from exc
            logger.warning(
                "GLPI API failed with %s, attempt %s of %s in %ss",
                type(exc).__name__,
                attempt,
                max_attempts,
                wait_seconds,
            )
            time.sleep(wait_seconds)
            wait_seconds *= 2
            attempt += 1
            continue

        status = resp.status_code
        if status == 401 and auth_client is not None:
            logger.warning(
                "Session token expired, obtaining new token and retrying request"
            )
            with _refresh_lock:
                token = auth_client.get_session_token(force_refresh=True)
                headers["Session-Token"] = token
            if attempt >= max_attempts:
                raise GLPIAuthError("Unauthorized after token refresh")
            attempt += 1
            continue

        if status == 403:
            logger.warning("Permission denied for %s", url)
            raise GLPIPermissionError(f"permission denied: {url}")

        if status >= 500:
            if attempt >= max_attempts:
                logger.error(
                    "GLPI API returned %s, exhausted %s attempts",
                    status,
                    max_attempts,
                )
                raise GLPIRetryError(f"status {status}")
            logger.warning(
                "GLPI API failed with %s, attempt %s of %s in %ss",
                status,
                attempt,
                max_attempts,
                wait_seconds,
            )
            time.sleep(wait_seconds)
            wait_seconds *= 2
            attempt += 1
            continue

        return resp

    raise GLPIRetryError(f"Max attempts reached for {url}")
