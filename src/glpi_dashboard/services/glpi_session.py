import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
import asyncio
import base64

import aiohttp
import contextlib
from aiohttp import ClientSession, TCPConnector

# Import custom exceptions and decorator from sibling module
from .exceptions import (
    GLPIAPIError,
    GLPIUnauthorizedError,
    HTTP_STATUS_ERROR_MAP,
    glpi_retry,
    parse_error,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIInternalServerError,
)

logger = logging.getLogger(__name__)


@dataclass
class Credentials:
    """
    Dataclass to hold GLPI API authentication credentials.

    Attributes:
        app_token: The GLPI application token.
        user_token: Optional GLPI user API token.
        username: Optional GLPI username for authentication.
        password: Optional GLPI password for authentication.
    """

    app_token: str
    user_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate that authentication credentials are provided.

        Either a ``user_token`` or ``username``/``password`` must be supplied.
        If both are present ``user_token`` is preferred.
        """
        auth_methods_count = sum(
            [
                1 if self.user_token else 0,
                1 if (self.username and self.password) else 0,
            ]
        )
        if auth_methods_count == 0:
            raise ValueError("Either user_token or username/password must be provided.")
        if auth_methods_count > 1:
            logger.warning(
                "Both user_token and username/password provided. "
                "Prioritizing user_token for initSession."
            )
            # Clear username/password if user_token is prioritized to ensure
            # single auth path
            self.username = None
            self.password = None


class GLPISession:
    """
    Manages a GLPI API session, handling authentication, token refreshing,
    and graceful session termination using an asynchronous context manager.
    """

    def __init__(
        self,
        base_url: str,
        credentials: Credentials,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: Union[int, aiohttp.ClientTimeout] = 300,
        refresh_interval: int = 3000,  # seconds, for proactive refresh if needed
    ) -> None:
        """
        Initializes the GLPI session manager.

        Args:
            base_url: The base URL of the GLPI API
                (e.g., "https://glpi.company.com/apirest.php").
            credentials: An instance of Credentials containing app_token and
                         either user_token or username/password.
            proxy: Optional proxy URL (e.g., "http://proxy.example.com:8080").
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
            timeout: Default timeout for HTTP requests in seconds.
            refresh_interval: Interval in seconds to proactively
                refresh the session token.
                Only applicable if using username/password for session initiation.
        """
        self.base_url = base_url.rstrip("/")
        self.credentials = credentials
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.refresh_interval = refresh_interval

        self._session_token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._last_refresh_time: float = 0.0
        self._refresh_lock = asyncio.Lock()

    def _resolve_timeout(self) -> aiohttp.ClientTimeout:
        """Return the timeout as an aiohttp.ClientTimeout object for aiohttp calls."""
        if isinstance(self.timeout, aiohttp.ClientTimeout):
            return self.timeout
        return aiohttp.ClientTimeout(total=float(self.timeout))

    async def _init_aiohttp_session(self) -> None:
        """Initializes the aiohttp ClientSession if it's not already open."""
        if self._session is None or self._session.closed:
            connector = TCPConnector(ssl=self.verify_ssl)
            self._session = ClientSession(connector=connector)
            logger.info("aiohttp ClientSession initialized.")

    async def _refresh_session_token(self) -> None:
        """
        Refreshes the GLPI session token by calling the initSession endpoint.
        Uses user_token if available, otherwise username/password.
        """
        async with self._refresh_lock:
            init_session_url = f"{self.base_url}/initSession"
            headers = {
                "Content-Type": "application/json",
                "App-Token": self.credentials.app_token,
            }

            if self.credentials.user_token:
                headers["Authorization"] = f"user_token {self.credentials.user_token}"
                logger.info("Attempting to initiate GLPI session with user_token...")
            elif self.credentials.username and self.credentials.password:
                cred = f"{self.credentials.username}:{self.credentials.password}"
                b64 = base64.b64encode(cred.encode()).decode()
                headers["Authorization"] = f"Basic {b64}"
                logger.info(
                    "Attempting to initiate GLPI session with username/password..."
                )
            else:
                raise ValueError(
                    "No valid authentication method "
                    "(user_token or username/password) provided."
                )

            try:
                if self._session is None:
                    self._session = aiohttp.ClientSession()

                async with self._session.get(
                    init_session_url,
                    headers=headers,
                    proxy=self.proxy,
                    timeout=self._resolve_timeout(),
                ) as response:
                    try:
                        # Raises aiohttp.ClientResponseError for 4xx/5xx
                        response.raise_for_status()
                    except aiohttp.ClientResponseError as e:
                        response_data = {}
                        response_text = ""
                        try:
                            response_data = await response.json()
                        except (aiohttp.ContentTypeError, ValueError):
                            with contextlib.suppress(Exception):
                                response_text = await response.text()
                        error_resp = getattr(e, "response", response)
                        error_class = HTTP_STATUS_ERROR_MAP.get(e.status, GLPIAPIError)
                        if self._session and not self._session.closed:
                            await self._session.close()
                            logger.info(
                                "aiohttp ClientSession closed due to init failure."
                            )
                        logger.error(
                            "initSession failed with status %s: %s",
                            e.status,
                            response_data or response_text,
                        )
                        raise error_class(
                            e.status,
                            parse_error(error_resp or response, response_data),
                            (
                                response_data or {"text": response_text}
                                if (response_data or response_text)
                                else None
                            ),
                        )

                    data = await response.json()
                    self._session_token = data.get("session_token")
                    if not self._session_token:
                        raise GLPIAPIError(
                            response.status,
                            "session_token not found in response",
                            data,
                        )
                    logger.info("GLPI session initiated successfully.")
                    # Record refresh time using the running loop
                    self._last_refresh_time = asyncio.get_running_loop().time()
            except aiohttp.ClientError as e:
                if self._session and not self._session.closed:
                    await self._session.close()
                    logger.info("aiohttp ClientSession closed due to init failure.")
                raise GLPIAPIError(
                    0,
                    f"Network or client error during session initiation: {e}",
                )

    async def _proactive_refresh_loop(self) -> None:
        """
        Proactively refreshes the session token before it expires.
        This loop runs only if authentication is via username/password for
        session initiation.
        """
        if self.credentials.user_token:
            logger.debug("Proactive refresh loop not needed for user_token.")
            return

        while True:
            await asyncio.sleep(self.refresh_interval)
            # Check if current token is older than refresh_interval
            if (
                self._session_token
                and (asyncio.get_running_loop().time() - self._last_refresh_time)
                >= self.refresh_interval
            ):
                logger.info("Proactively refreshing GLPI session token.")
                try:
                    await self._refresh_session_token()
                except Exception as e:
                    logger.error("Failed to proactively refresh session token: %s", e)
                    # In a production system, consider exponential backoff or
                    # circuit breaking here.

    async def __aenter__(self) -> "GLPISession":
        """
        Enters the asynchronous context, initiating the GLPI session.
        """
        await self._init_aiohttp_session()
        await self._refresh_session_token()

        # Start proactive refresh task only if using username/password flow
        if not self.credentials.user_token:
            self._refresh_task = asyncio.create_task(self._proactive_refresh_loop())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exits the asynchronous context, gracefully killing the GLPI session.
        """
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                logger.info("Proactive refresh task cancelled.")

        if self._session_token:
            await self._kill_session()

        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("aiohttp ClientSession closed.")

    async def _kill_session(self) -> None:
        """Kills the current GLPI session by calling the killSession endpoint."""
        if not self._session_token:
            logger.warning("No session token to kill.")
            return

        kill_session_url = f"{self.base_url}/killSession"
        headers = {
            "Content-Type": "application/json",
            "Session-Token": self._session_token,
            "App-Token": self.credentials.app_token,
        }
        logger.info("Attempting to kill GLPI session...")
        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()

            async with self._session.get(
                kill_session_url,
                headers=headers,
                proxy=self.proxy,
                timeout=self._resolve_timeout(),
            ) as response:
                response.raise_for_status()
                logger.info("GLPI session killed successfully.")
        except aiohttp.ClientResponseError as e:
            logger.error(f"Network or client error during session termination: {e}")
        finally:
            self._session_token = None  # Always clear token after attempt to kill

    @glpi_retry(max_retries=5)  # Apply the retry decorator here
    async def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Union[str, int, float]]] = None,
        retry_on_401: bool = True,
        max_401_retries: int = 1,  # One retry after initial 401
    ) -> Dict[str, Any]:
        """
        Makes an authenticated request to the GLPI API.

        This method includes specific retry logic for 401 Unauthorized errors
        (token refresh) and leverages the ``@glpi_retry`` decorator for other
        transient errors (429, 500, network issues).

        Args:
            method: HTTP method (e.g., "GET", "POST", "PUT", "DELETE").
            endpoint: The API endpoint relative to the base URL (e.g., "Ticket/").
            headers: Additional headers for the request.
            json_data: JSON payload for POST/PUT requests.
            params: Query parameters for the request.
            retry_on_401: Whether to attempt token refresh and retry on 401
                Unauthorized.
            max_401_retries: Maximum number of retries for 401 errors
                (specific to token refresh).

        Returns:
            The JSON response from the API.

        Raises:
            GLPIAPIError: If the API returns an error status code or other issues occur.
        """
        if self._session is None or self._session.closed:
            await self._init_aiohttp_session()  # Ensure session is open

        full_url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "App-Token": self.credentials.app_token,
        }
        if self._session_token:
            request_headers["Session-Token"] = self._session_token
        if headers:
            request_headers.update(headers)

        for attempt in range(max_401_retries + 1):
            try:
                current_headers = request_headers.copy()
                if self._session is None:
                    self._session = aiohttp.ClientSession()

                async with self._session.request(
                    method,
                    full_url,
                    headers=current_headers,
                    json=json_data,
                    params=params,
                    proxy=self.proxy,
                    timeout=self._resolve_timeout(),
                ) as response:
                    if (
                        response.status == 401
                        and retry_on_401
                        and attempt < max_401_retries
                    ):
                        logger.warning(
                            "Received 401 Unauthorized. Attempting to refresh "
                            "session token..."
                        )
                        try:
                            await self._refresh_session_token()
                        except GLPIUnauthorizedError:
                            raise GLPIUnauthorizedError(
                                401,
                                "Failed to authenticate after multiple retries",
                            )
                        if self._session_token:  # Update header for retry
                            request_headers["Session-Token"] = self._session_token
                        continue  # Retry the request

                    # Raises aiohttp.ClientResponseError for 4xx/5xx
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                response_data = {}
                with contextlib.suppress(aiohttp.ContentTypeError, ValueError):
                    response_data = await response.json()
                error_resp = getattr(e, "response", response)
                error_class = HTTP_STATUS_ERROR_MAP.get(e.status, GLPIAPIError)
                # Raise the specific GLPIAPIError, which the @glpi_retry
                # decorator will then catch
                raise error_class(
                    e.status,
                    parse_error(error_resp, response_data),
                    response_data,
                )
            except aiohttp.ClientError as e:
                # This catches network-level errors before an HTTP status is received
                # The @glpi_retry decorator will handle retries for these as well
                raise GLPIAPIError(
                    0, f"Network or client error during API request: {e}"
                )
            except Exception as e:
                if isinstance(e, GLPIAPIError):
                    raise
                # Catch any other unexpected exceptions and wrap them
                raise GLPIAPIError(0, f"An unexpected error occurred: {e}")

        # If all 401 retries fail
        raise GLPIUnauthorizedError(
            401, "Failed to authenticate after multiple 401 retries."
        )

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Performs a GET request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/").
            params: Query parameters for the request.
            headers: Additional headers for the request.

        Returns:
            The JSON response from the API.
        """
        return await self._request("GET", endpoint, headers=headers, params=params)

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Performs a POST request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/").
            json_data: JSON payload to send in the request body.
            headers: Additional headers for the request.
        """
        return await self._request(
            "POST", endpoint, headers=headers, json_data=json_data
        )

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Performs a PUT request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/123").
            json_data: JSON payload to send in the request body.
            headers: Additional headers for the request.
        """
        return await self._request(
            "PUT", endpoint, headers=headers, json_data=json_data
        )

    async def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Performs a DELETE request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/123").
            headers: Additional headers for the request.
        """
        return await self._request("DELETE", endpoint, headers=headers)

    async def get_all(self, itemtype: str, **params: Any) -> list[dict]:
        """Retrieve all items for a given GLPI type using pagination."""

        from glpi_dashboard.config.settings import FETCH_PAGE_SIZE

        params = {**params, "expand_dropdowns": 1}
        endpoint = (
            f"search/{itemtype}" if not itemtype.startswith("search/") else itemtype
        )
        results: list[dict] = []
        offset = 0
        while True:
            page_params = {
                **params,
                "range": f"{offset}-{offset + FETCH_PAGE_SIZE - 1}",
            }
            data = await self.get(endpoint, params=page_params)
            page = data.get("data", data)
            if isinstance(page, dict):
                page = [page]
            results.extend(page)
            if len(page) < FETCH_PAGE_SIZE:
                break
            offset += FETCH_PAGE_SIZE
        return results


__all__ = [
    "GLPISession",
    "Credentials",
    "GLPIUnauthorizedError",
    "GLPIBadRequestError",
    "GLPIForbiddenError",
    "GLPINotFoundError",
    "GLPITooManyRequestsError",
    "GLPIInternalServerError",
]
