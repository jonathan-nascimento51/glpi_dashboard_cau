import asyncio
import contextlib
import inspect
import json
import logging
import os
import ssl
from types import TracebackType
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlsplit, urlunsplit

import aiohttp
from aiohttp import BasicAuth, ClientResponse, ClientSession, TCPConnector
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.core.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)

# Import custom exceptions and decorator from sibling module
from backend.domain.exceptions import (
    HTTP_STATUS_ERROR_MAP,
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GLPIInternalServerError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIUnauthorizedError,
)
from backend.domain.tool_error import ToolError
from shared.utils.resilience import call_with_breaker, retry_api_call

logger = logging.getLogger(__name__)

CONTENT_TYPE_JSON = "application/json"


def parse_error(response: ClientResponse, data: Optional[dict[str, Any]] = None) -> str:
    """Extract and return a user-friendly error message from the response."""
    if data and "message" in data:
        return data["message"]
    return f"Error {response.status}: {response.reason}"


def mask_proxy_url(url: Optional[str]) -> Optional[str]:
    """Return a version of ``url`` with the password obscured."""
    if not url:
        return url
    try:
        parsed = urlsplit(url)
        if parsed.password:
            user = parsed.username or ""
            host = parsed.hostname or ""
            port = f":{parsed.port}" if parsed.port else ""
            netloc = f"{user}:***@{host}{port}" if user else f"***@{host}{port}"
            return urlunsplit(
                (parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment)
            )
        return url
    except Exception:
        return url


class Credentials(BaseModel):
    """Authentication data for the GLPI REST API.

    Use this model when calling GLPI tools so credentials are validated before
    any network request is attempted.
    """

    app_token: str = Field(..., description="GLPI application token")
    user_token: Optional[str] = Field(
        default=None, description="Optional user API token"
    )
    username: Optional[str] = Field(
        default=None, description="GLPI username used when no token is provided"
    )
    password: Optional[str] = Field(
        default=None,
        description="GLPI password used together with ``username``",
    )

    @model_validator(mode="after")
    def _check_auth(self) -> "Credentials":
        """Ensure at least one authentication method is supplied."""
        auth_methods = sum(
            [
                1 if self.user_token else 0,
                1 if (self.username and self.password) else 0,
            ]
        )
        if auth_methods == 0:
            raise ValueError("Either user_token or username/password must be provided.")
        if auth_methods > 1:
            logger.debug(
                "Both user_token and username/password provided. "
                "Prioritizing user_token."
            )
            self.username = None
            self.password = None
        return self


class SessionParams(BaseModel):
    """Input data for creating :class:`GLPISession`."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_url: str = Field(..., description="GLPI REST base URL")
    credentials: Credentials
    proxy: Optional[str] = Field(
        default_factory=lambda: os.environ.get("HTTP_PROXY"),
        description="Optional proxy URL; defaults to HTTP_PROXY env var",
    )
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_context: Optional[ssl.SSLContext] = Field(
        default=None, description="Custom SSL context for TLS connections"
    )
    timeout: Union[int, aiohttp.ClientTimeout] = Field(
        default=300, description="Request timeout in seconds"
    )
    refresh_interval: int = Field(
        default=3000,
        description="Interval in seconds to proactively refresh the session",
    )


class GLPISession:
    """Manage an authenticated session with the GLPI REST API.

    This tool is ideal for background workers that need long-lived access to the
    API. It transparently refreshes tokens and cleans up network resources when
    used as an async context manager.
    """

    def __init__(
        self,
        base_url: str,
        credentials: Credentials,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        ssl_context: Optional[ssl.SSLContext] = None,
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
                Defaults to the ``HTTP_PROXY`` environment variable when unset.
            verify_ssl: Whether to verify SSL certificates. Defaults to True.
            ssl_context: Custom :class:`ssl.SSLContext` to use when verifying
                SSL certificates.
            timeout: Default timeout for HTTP requests in seconds.
            refresh_interval: Interval in seconds to proactively
                refresh the session token.
                Only applicable if using username/password for session initiation.
        """
        self.base_url = base_url.rstrip("/")
        self.credentials = credentials
        self.proxy = proxy or os.environ.get("HTTP_PROXY")
        self.verify_ssl = verify_ssl
        self.ssl_ctx = ssl_context
        self.timeout = timeout
        self.refresh_interval = refresh_interval

        self._session_token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._refresh_task: Optional[asyncio.Task[None]] = None
        self._last_refresh_time: float = 0.0
        self._refresh_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        # Track whether the current session was created using user_token or
        # username/password. This determines if killSession should be called on
        # exit. Defaults to ``bool(credentials.user_token)`` but is updated on
        # each token refresh.
        self._using_user_token: bool = bool(credentials.user_token)

    def _resolve_timeout(self) -> aiohttp.ClientTimeout:
        """Return the timeout as an aiohttp.ClientTimeout object for aiohttp calls."""
        if isinstance(self.timeout, aiohttp.ClientTimeout):
            return self.timeout
        return aiohttp.ClientTimeout(total=float(self.timeout))

    def _init_aiohttp_session(self) -> None:
        """Initializes the aiohttp ClientSession if it's not already open."""
        if self._session is None or self._session.closed:
            if not self.verify_ssl:
                connector = TCPConnector(ssl=False)
            elif self.ssl_ctx is not None:
                connector = TCPConnector(ssl=self.ssl_ctx)
            else:
                connector = TCPConnector()
            self._session = ClientSession(connector=connector, trust_env=True)
            if proxy_info := mask_proxy_url(self.proxy):
                logger.info(
                    "aiohttp ClientSession initialized via proxy %s", proxy_info
                )
            else:
                logger.info("aiohttp ClientSession initialized.")

    @retry_api_call
    async def _refresh_session_token(self) -> None:
        """
        Refresh the GLPI session token by calling the ``initSession`` endpoint.

        The aiohttp session is (re)created via ``_init_aiohttp_session`` to
        guarantee a fresh connection when needed.
        """
        async with self._refresh_lock:
            self._init_aiohttp_session()
            assert self._session is not None
            init_session_url = f"{self.base_url}/initSession"
            headers = self._build_init_headers()
            self._set_auth_headers(headers)
            try:
                self._init_aiohttp_session()
                assert self._session is not None
                get_kwargs = self._build_get_kwargs()
                async with self._session.get(
                    init_session_url,
                    headers=headers,
                    **get_kwargs,
                ) as response:
                    await self._handle_init_response(response)
            except aiohttp.ClientError as e:
                await self._handle_client_error(e)

    def _build_init_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": CONTENT_TYPE_JSON,
            "App-Token": self.credentials.app_token,
        }

    def _set_auth_headers(self, headers: Dict[str, str]) -> None:
        if self.credentials.user_token:
            headers["Authorization"] = f"user_token {self.credentials.user_token}"
            logger.info("Attempting to initiate GLPI session with user_token...")
            self._using_user_token = True
        elif self.credentials.username and self.credentials.password:
            basic_auth = BasicAuth(
                self.credentials.username,
                self.credentials.password,
            )
            headers["Authorization"] = basic_auth.encode()
            logger.info("Attempting to initiate GLPI session with username/password...")
            self._using_user_token = False
        else:
            raise ValueError(
                "No valid authentication method "
                "(user_token or username/password) provided."
            )

    def _build_get_kwargs(self) -> Dict[str, Any]:
        get_kwargs: Dict[str, Any] = {
            "proxy": self.proxy,
            "timeout": self._resolve_timeout(),
        }
        if not self.verify_ssl:
            get_kwargs["ssl"] = False
        elif self.ssl_ctx is not None:
            get_kwargs["ssl"] = self.ssl_ctx
        return get_kwargs

    async def _handle_init_response(self, response: aiohttp.ClientResponse) -> None:
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            await self._handle_init_error(e, response)
        data = await response.json()
        self._session_token = data.get("session_token")
        if not self._session_token:
            raise GLPIAPIError(
                response.status,
                "session_token not found in response",
                data,
            )
        logger.info("GLPI session initiated successfully.")
        self._last_refresh_time = asyncio.get_running_loop().time()

    async def _handle_init_error(
        self, e: aiohttp.ClientResponseError, response: aiohttp.ClientResponse
    ) -> None:

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
            logger.info("aiohttp ClientSession closed due to init failure.")
        logger.error(
            "initSession returned status %s: %s",
            e.status,
            json.dumps(response_data) if response_data else response_text,
        )
        raise error_class(
            e.status,
            parse_error(error_resp or response),
            (
                response_data or {"text": response_text}
                if (response_data or response_text)
                else None
            ),
        ) from e

    async def _handle_client_error(self, e: aiohttp.ClientError) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("aiohttp ClientSession closed due to init failure.")
        proxy_info = mask_proxy_url(self.proxy)
        raise GLPIAPIError(
            0,
            (
                f"Network or client error during session initiation: {e}"
                f" via proxy {proxy_info}"
                if proxy_info
                else f"Network or client error during session initiation: {e}"
            ),
        ) from e

    async def _proactive_refresh_loop(self) -> None:
        """
        Proactively refreshes the session token before it expires.
        This loop runs only if authentication is via username/password for
        session initiation.
        """
        if self.credentials.user_token:
            logger.debug("Proactive refresh loop not needed for user_token.")
            return

        while not self._shutdown_event.is_set():
            start = asyncio.get_running_loop().time()
            elapsed = 0.0
            # Sleep in short increments so we can exit early if needed
            while elapsed < self.refresh_interval and not self._shutdown_event.is_set():
                to_sleep = min(1.0, self.refresh_interval - elapsed)
                await asyncio.sleep(to_sleep)
                elapsed = asyncio.get_running_loop().time() - start

            if self._shutdown_event.is_set():
                break

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
                    logger.error("failed to proactively refresh session token: %s", e)
                    # In a production system, consider exponential backoff or
                    # circuit breaking here.

    async def __aenter__(self) -> "GLPISession":
        """
        Enters the asynchronous context, initiating the GLPI session.
        """
        self._init_aiohttp_session()
        await self._refresh_session_token()

        # Start proactive refresh task only if using username/password flow
        if not self.credentials.user_token:
            self._shutdown_event.clear()
            self._refresh_task = asyncio.create_task(self._proactive_refresh_loop())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional["TracebackType"],
    ) -> None:
        """
        Exits the asynchronous context, gracefully killing the GLPI session.
        Exits the asynchronous context, gracefully killing the GLPI session.

        Sets ``_shutdown_event`` so that the proactive refresh loop can
        terminate promptly before cleaning up network resources.
        """
        self._shutdown_event.set()
        if self._refresh_task:
            self._refresh_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._refresh_task
            logger.info("Proactive refresh task cancelled.")

        if self._session_token and not self._using_user_token:
            await self._kill_session()
        else:
            # Ensure token is cleared even when killSession is skipped
            self._session_token = None

        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("aiohttp ClientSession closed.")

    async def close(self) -> None:
        """Public method to close the session without a context manager."""
        await self.__aexit__(None, None, None)

    @retry_api_call
    async def _kill_session(self) -> None:
        """Kills the current GLPI session by calling the killSession endpoint.

        If no session token is set, this method performs no action and returns
        immediately.
        """
        if not self._session_token:
            logger.info("No session token to kill.")
            return

        kill_session_url = f"{self.base_url}/killSession"
        headers = {
            "Content-Type": CONTENT_TYPE_JSON,
            "Session-Token": self._session_token,
            "App-Token": self.credentials.app_token,
        }
        logger.info("Attempting to kill GLPI session...")
        try:
            self._init_aiohttp_session()
            assert self._session is not None

            get_kwargs: dict[str, Any] = {
                "headers": headers,
                "timeout": self._resolve_timeout(),
            }
            if self.proxy is not None:
                get_kwargs["proxy"] = self.proxy
            if not self.verify_ssl:
                get_kwargs["ssl"] = False
            elif self.ssl_ctx is not None:
                get_kwargs["ssl"] = self.ssl_ctx

            async with self._session.get(kill_session_url, **get_kwargs) as resp:
                resp.raise_for_status()
                logger.info("GLPI session killed successfully.")
        except aiohttp.ClientResponseError as e:
            proxy_info = mask_proxy_url(self.proxy)
            logger.error(
                "Network or client error during session termination: %s via proxy %s",
                e,
                proxy_info,
            )
        finally:
            self._session_token = None  # Always clear token after attempt to kill

    @call_with_breaker
    @retry_api_call  # Apply the retry decorator here
    async def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Union[str, int, float]]] = None,
        retry_on_401: bool = True,
        max_401_retries: int = 1,
        return_headers: bool = False,
    ) -> Any:
        """
        Makes an authenticated request to the GLPI API with retry logic for 401 errors.
        """
        if self._session is None or self._session.closed:
            self._init_aiohttp_session()

        full_url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._build_request_headers(headers)
        return await self._request_with_retries(
            method,
            full_url,
            request_headers,
            json_data,
            params,
            retry_on_401,
            max_401_retries,
            return_headers,
            headers,
        )

    async def _request_with_retries(
        self,
        method: str,
        full_url: str,
        request_headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Union[str, int, float]]],
        retry_on_401: bool,
        max_401_retries: int,
        return_headers: bool,
        orig_headers: Optional[Dict[str, str]],
    ) -> Any:
        for attempt in range(max_401_retries + 1):
            try:
                return await self._execute_request(
                    method,
                    full_url,
                    request_headers,
                    json_data,
                    params,
                    return_headers,
                    retry_on_401,
                    attempt,
                    max_401_retries,
                )
            except GLPIUnauthorizedError:
                if retry_on_401 and attempt < max_401_retries:  # noqa: B007
                    logger.warning(
                        "Received 401 Unauthorized. "
                        "Attempting to refresh session token...",
                    )
                    await self._handle_unauthorized()
                    request_headers = self._build_request_headers(orig_headers)
                    continue
                raise
            except aiohttp.ClientError as e:
                self._raise_client_error(e)
            except Exception as e:  # noqa: B902
                if isinstance(e, GLPIAPIError):
                    raise
                raise GLPIAPIError(0, f"An unexpected error occurred: {e}") from e
        raise GLPIUnauthorizedError(
            401, "Failed to authenticate after multiple 401 retries."
        )

    def _build_request_headers(
        self, headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        request_headers: Dict[str, str] = {
            "Content-Type": CONTENT_TYPE_JSON,
            "App-Token": self.credentials.app_token,
        }
        if self._session_token:
            request_headers["Session-Token"] = self._session_token
        if headers:
            request_headers |= headers
        return request_headers

    async def _execute_request(
        self,
        method: str,
        full_url: str,
        request_headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Union[str, int, float]]],
        return_headers: bool,
        retry_on_401: bool,
        attempt: int,
        max_401_retries: int,
    ) -> Any:
        self._init_aiohttp_session()
        assert self._session is not None
        request_kwargs: Dict[str, Any] = {
            "headers": request_headers,
            "json": json_data,
            "params": params,
            "proxy": self.proxy,
            "timeout": self._resolve_timeout(),
        }
        if not self.verify_ssl:
            request_kwargs["ssl"] = False
        elif self.ssl_ctx is not None:
            request_kwargs["ssl"] = self.ssl_ctx

        request_ctx = self._session.request(
            method,
            full_url,
            **request_kwargs,
        )
        if inspect.isawaitable(request_ctx):
            request_ctx = await request_ctx
        async with request_ctx as response:
            if response.status == 401 and retry_on_401 and attempt < max_401_retries:
                raise GLPIUnauthorizedError(401, "401 Unauthorized")
            try:
                response.raise_for_status()
                data = await response.json()
                return (data, dict(response.headers)) if return_headers else data
            except aiohttp.ClientResponseError as e:
                await self._handle_response_error(e, response)

    async def _handle_unauthorized(self):
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        # Attempt to refresh the session token. If it fails, re-raise the
        # GLPIUnauthorizedError to propagate the authentication failure.
        await self._refresh_session_token()

    async def _handle_response_error(
        self,
        e: aiohttp.ClientResponseError,
        response: aiohttp.ClientResponse,
    ):
        response_data: Dict[str, Any] = {}

        response_text = ""
        try:
            response_data = await response.json()
        except (aiohttp.ContentTypeError, ValueError):
            with contextlib.suppress(Exception):
                response_text = await response.text()
        error_class = HTTP_STATUS_ERROR_MAP.get(e.status, GLPIAPIError)
        raise error_class(
            e.status,
            parse_error(response, response_data),
            response_data or {"text": response_text},
        ) from e

    def _raise_client_error(self, e: aiohttp.ClientError):
        proxy_info = mask_proxy_url(self.proxy)
        msg = f"Network or client error during API request: {e}"
        if proxy_info:
            msg += f" via proxy {proxy_info}"
        raise GLPIAPIError(0, msg) from e

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        return_headers: bool = False,
    ) -> Any:
        """
        Performs a GET request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/").
            params: Query parameters for the request.
            headers: Additional headers for the request.

        Returns:
            The JSON response from the API.
        """
        return await self._request(
            "GET",
            endpoint,
            headers=headers,
            params=params,
            return_headers=return_headers,
        )

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        return_headers: bool = False,
    ) -> Any:
        """
        Performs a POST request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/").
            json_data: JSON payload to send in the request body.
            headers: Additional headers for the request.
        """
        return await self._request(
            "POST",
            endpoint,
            headers=headers,
            json_data=json_data,
            return_headers=return_headers,
        )

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        return_headers: bool = False,
    ) -> Any:
        """
        Performs a PUT request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/123").
            json_data: JSON payload to send in the request body.
            headers: Additional headers for the request.
        """
        return await self._request(
            "PUT",
            endpoint,
            headers=headers,
            json_data=json_data,
            return_headers=return_headers,
        )

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        *,
        return_headers: bool = False,
    ) -> Any:
        """
        Performs a DELETE request to the GLPI API.

        Args:
            endpoint: The API endpoint (e.g., "Ticket/123").
            headers: Additional headers for the request.
        """
        return await self._request(
            "DELETE", endpoint, headers=headers, return_headers=return_headers
        )

    async def get_all(self, itemtype: str, **params: Any) -> List[Dict[str, Any]]:
        """Retrieve all items for a given GLPI type using pagination."""

        from backend.core.settings import FETCH_PAGE_SIZE

        params = {**params, "expand_dropdowns": 1}
        endpoint = itemtype if itemtype.startswith("search/") else f"search/{itemtype}"
        results: List[Dict[str, Any]] = []
        offset = 0
        while True:
            page_params: Dict[str, Any] = {
                **params,
                "range": f"{offset}-{offset + FETCH_PAGE_SIZE - 1}",
            }
            # The 'get' method returns 'Any'. We annotate 'data' with a more specific
            # type to help the type checker understand its structure.
            data: Union[Dict[str, Any], List[Any]] = await self.get(
                endpoint, params=page_params
            )
            page: Any = data.get("data", data) if isinstance(data, dict) else data
            if isinstance(page, dict):
                page = [page]
            results.extend(page)
            if len(page) < FETCH_PAGE_SIZE:
                break
            offset += FETCH_PAGE_SIZE
        return results

    # ------------------------------------------------------------------
    # Convenience helpers matching the deprecated clients
    # ------------------------------------------------------------------
    async def search_rest(
        self, itemtype: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a REST ``search`` query."""

        return await self.get(f"search/{itemtype}", params=params)

    async def list_search_options(self, itemtype: str) -> Dict[str, Any]:
        """Retrieve search fields for ``itemtype``."""

        return await self.get(f"listSearchOptions/{itemtype}")

    async def get_all_paginated(
        self, itemtype: str, page_size: int = 100, **params: Any
    ) -> List[Dict[str, Any]]:
        """Return all items for ``itemtype`` using a resilient page loop."""
        base_params: Dict[str, Any] = {**params, "expand_dropdowns": 1}
        endpoint = itemtype if itemtype.startswith("search/") else f"search/{itemtype}"
        results: List[Dict[str, Any]] = []
        offset = 0

        while True:
            page_params: Dict[str, Any] = {
                **base_params,
                "range": f"{offset}-{offset + page_size - 1}",
            }
            # The get method returns the JSON body directly
            data: Union[Dict[str, Any], List[Any]] = await self.get(
                endpoint, params=page_params
            )

            # Handle inconsistent API responses (dict vs list)
            page_items: Union[List[Any], Dict[str, Any]] = (
                data.get("data", data) if isinstance(data, dict) else data
            )

            # Ensure page_items is always a list
            if isinstance(page_items, dict):
                page_items = [page_items]

            if not page_items:  # Stop if the page is empty
                break

            results.extend(page_items)

            if len(page_items) < page_size:  # Stop if we received less than a full page
                break

        return results

    async def query_graphql(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a GraphQL query to the GLPI server."""

        payload: Dict[str, Any] = {"query": query, "variables": variables or {}}
        data = await self.post("graphql", json_data=payload)
        if "errors" in data:
            msg = data["errors"][0].get("message", "GraphQL query failed")
            raise GLPIAPIError(0, msg, data)
        return data.get("data", data) or {}


async def open_session_tool(params: SessionParams) -> str:
    """Validate credentials by opening and closing a session.

    This tool is typically called by orchestrators in the multi-agent
    pipeline defined in ``AGENTS.md`` to confirm connectivity with the GLPI
    server.  It returns ``"ok"`` when a session can be established. On
    failure it returns a JSON string ``{"error": {"message": str, "details": str}}``.
    """

    try:
        async with GLPISession(**params.model_dump()) as _:
            return "ok"
    except Exception as exc:  # pragma: no cover - tool usage
        err = ToolError("failed to open session", str(exc))
        return json.dumps({"error": err.dict()})


async def index_all_paginated(
    itemtype: str, page_size: int = 100, **params: Any
) -> List[Dict[str, Any]]:
    """Fetch all records for ``itemtype`` using a short-lived session."""
    creds = Credentials(
        app_token=str(GLPI_APP_TOKEN),
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    session = GLPISession(GLPI_BASE_URL, creds)
    async with session:
        return await session.get_all_paginated(itemtype, page_size=page_size, **params)


__all__ = [
    "GLPISession",
    "Credentials",
    "SessionParams",
    "open_session_tool",
    "GLPIUnauthorizedError",
    "GLPIBadRequestError",
    "GLPIForbiddenError",
    "GLPINotFoundError",
    "GLPITooManyRequestsError",
    "GLPIInternalServerError",
    "index_all_paginated",
]
