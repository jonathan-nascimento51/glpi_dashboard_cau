"""Asynchronous REST client for GLPI built on ``httpx``.

This module exposes :class:`GLPIClient`, a lightweight wrapper around the
GLPI REST and GraphQL endpoints.  It handles authentication, persists the
session token and automatically forwards the required ``App-Token`` and
``Session-Token`` headers once a session is established.

Example
-------
```python
import asyncio
from glpi_dashboard.services.glpi_rest_client import GLPIClient


async def main() -> None:
    client = GLPIClient(
        "https://glpi.example.com/apirest.php",
        app_token="APP_TOKEN",
        user_token="USER_TOKEN",
    )
    await client.init_session()
    data = await client.search_rest("Ticket", params={"criteria[0][field]": 1})
    print(data)
    await client.close()


asyncio.run(main())
```
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import random
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from .exceptions import GLPIAPIError

logger = logging.getLogger(__name__)


class RestClientParams(BaseModel):
    """Parameters for :class:`GLPIClient` construction."""

    base_url: str = Field(..., description="GLPI REST base URL")
    app_token: str
    user_token: Optional[str] = Field(default=None, description="User API token")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    retry_max: int = Field(default=5, description="Maximum retry attempts")
    retry_base_delay: float = Field(
        default=0.1, description="Base delay for exponential backoff"
    )


class GraphQLQueryParams(RestClientParams):
    """Input parameters for :func:`graphql_query_tool`.

    Extends :class:`RestClientParams` with the GraphQL ``query`` to execute.
    """

    query: str = Field(..., description="GraphQL query string")


class GLPIClient:
    """Asynchronous client for the GLPI REST API.

    Use this tool when non-blocking access to GLPI is required, for example in a
    FastAPI worker or background task. It handles retries and session management
    automatically.
    """

    def __init__(
        self,
        base_url: str,
        app_token: str,
        user_token: Optional[str] = None,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        retry_max: int = 5,
        retry_base_delay: float = 0.1,
    ) -> None:
        """Instantiate the client.

        Parameters
        ----------
        base_url:
            Base URL of the GLPI REST API (e.g.
            ``https://glpi.example.com/apirest.php``).
        app_token:
            The application token generated in GLPI.
        user_token:
            Optional API token of the user.  Alternatively ``username`` and
            ``password`` can be supplied to :meth:`init_session`.
        timeout:
            Request timeout in seconds.
        verify_ssl:
            Whether to verify SSL certificates when making requests.
        retry_max:
            Maximum number of retry attempts for transient errors.
        retry_base_delay:
            Base delay (seconds) used for exponential backoff between retries.
        """

        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.user_token = user_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.retry_max = retry_max
        self.retry_base_delay = retry_base_delay
        self._session_token: Optional[str] = None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify_ssl,
            headers={"App-Token": self.app_token},
        )

    async def close(self) -> None:
        """Close the underlying ``httpx`` client."""

        await self._client.aclose()

    async def _request_with_retry(
        self, method: str, url: str, **kwargs: Any
    ) -> httpx.Response:
        """Perform an HTTP request with exponential backoff retries."""

        for attempt in range(self.retry_max + 1):
            try:
                resp = await self._client.request(method, url, **kwargs)
            except (httpx.TimeoutException, httpx.HTTPError) as exc:
                if attempt < self.retry_max:
                    delay = self.retry_base_delay * (2**attempt)
                    jitter = random.uniform(0, delay)
                    logger.warning(
                        json.dumps(
                            {
                                "event": "glpi_retry",
                                "attempt": attempt + 1,
                                "status": 0,
                            }
                        )
                    )
                    await asyncio.sleep(delay + jitter)
                    continue
                raise GLPIAPIError(0, f"HTTP error during {url}: {exc}") from exc

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < self.retry_max:
                    delay = self.retry_base_delay * (2**attempt)
                    jitter = random.uniform(0, delay)
                    logger.warning(
                        json.dumps(
                            {
                                "event": "glpi_retry",
                                "attempt": attempt + 1,
                                "status": resp.status_code,
                            }
                        )
                    )
                    await asyncio.sleep(delay + jitter)
                    continue

            return resp

        raise GLPIAPIError(0, f"API call failed after {self.retry_max} retries.")

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------
    async def init_session(
        self,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Open a session and persist the ``Session-Token`` header.

        At least one authentication method is required.  Either provide ``user_token``
        at construction time or supply ``username`` and ``password`` here.

        Raises
        ------
        GLPIAPIError
            If the server returns an error message or if a timeout occurs.
        """

        headers = {"App-Token": self.app_token}
        if self.user_token:
            headers["Authorization"] = f"user_token {self.user_token}"
        elif username and password:
            token = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        else:
            raise ValueError("Credentials required to init session")

        try:
            resp = await self._client.get("initSession", headers=headers)
        except httpx.TimeoutException as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"Timeout during initSession: {exc}") from exc
        except httpx.HTTPError as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"HTTP error during initSession: {exc}") from exc

        data = resp.json()
        if data.get("message") == "ERROR_JSON_PAYLOAD_FORBIDDEN":
            raise GLPIAPIError(resp.status_code, data["message"], data)
        if resp.status_code >= 400:
            raise GLPIAPIError(
                resp.status_code, data.get("message", resp.reason_phrase), data
            )

        self._session_token = data.get("session_token")
        if self._session_token:
            self._client.headers["Session-Token"] = self._session_token
        else:
            raise GLPIAPIError(resp.status_code, "session_token missing", data)

    # ------------------------------------------------------------------
    # REST helpers
    # ------------------------------------------------------------------
    async def search_rest(
        self, itemtype: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a REST ``search`` query.

        Parameters
        ----------
        itemtype:
            The GLPI item type to search (e.g. ``Ticket``).
        params:
            Optional dictionary of query parameters understood by the GLPI API.

        Returns
        -------
        dict
            Parsed JSON response from the API.

        Raises
        ------
        GLPIAPIError
            If the API responds with an error or the request times out.
        """

        url = f"search/{itemtype}"
        resp = await self._request_with_retry("GET", url, params=params)

        data = resp.json()
        if data.get("message") == "ERROR_JSON_PAYLOAD_FORBIDDEN":
            raise GLPIAPIError(resp.status_code, data["message"], data)
        if resp.status_code >= 400:
            raise GLPIAPIError(
                resp.status_code, data.get("message", resp.reason_phrase), data
            )
        return data

    async def list_search_options(self, itemtype: str) -> Dict[str, Any]:
        """Retrieve available search fields for ``itemtype``."""

        url = f"listSearchOptions/{itemtype}"
        resp = await self._request_with_retry("GET", url)

        data = resp.json()
        if data.get("message") == "ERROR_JSON_PAYLOAD_FORBIDDEN":
            raise GLPIAPIError(resp.status_code, data["message"], data)
        if resp.status_code >= 400:
            raise GLPIAPIError(
                resp.status_code, data.get("message", resp.reason_phrase), data
            )
        return data

    async def get_all_paginated(
        self, itemtype: str, page_size: int = 100, **params: Any
    ) -> List[Dict[str, Any]]:
        """Return all items for ``itemtype`` using a resilient page loop."""

        logger.info("Starting paginated fetch for %s with params %s", itemtype, params)

        results: List[Dict[str, Any]] = []
        offset = 0
        base_params = {**params, "expand_dropdowns": 1}
        endpoint = itemtype if itemtype.startswith("search/") else f"search/{itemtype}"

        while True:
            page_params = {
                **base_params,
                "range": f"{offset}-{offset + page_size - 1}",
            }

            try:
                resp = await self._request_with_retry(
                    "GET", endpoint, params=page_params
                )
            except httpx.HTTPError as exc:
                logger.critical("Pagination aborted: %s", exc)
                break

            data = resp.json()
            if data.get("message") == "ERROR_JSON_PAYLOAD_FORBIDDEN":
                raise GLPIAPIError(resp.status_code, data["message"], data)
            if resp.status_code >= 400 and resp.status_code != 429:
                raise GLPIAPIError(
                    resp.status_code,
                    data.get("message", resp.reason_phrase),
                    data,
                )

            page_items = data.get("data", data)
            if isinstance(page_items, dict):
                page_items = [page_items]
            page_items = [i for i in page_items if isinstance(i, dict)]

            if not page_items:
                logger.info("No items in page; stopping pagination for %s", itemtype)
                break

            results.extend(page_items)

            offset += page_size
            await asyncio.sleep(0.1)

        logger.info("Pagination finished for %s: %d items", itemtype, len(results))
        return results

    # ------------------------------------------------------------------
    # GraphQL helper
    # ------------------------------------------------------------------
    async def query_graphql(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a GraphQL query to the GLPI server.

        Parameters
        ----------
        query:
            GraphQL query string.
        variables:
            Optional mapping of variables for the query.

        Returns
        -------
        dict
            The ``data`` section of the GraphQL response.

        Raises
        ------
        GLPIAPIError
            If the API returns an error, the query produces GraphQL errors or a
            timeout occurs.
        """

        payload = {"query": query, "variables": variables or {}}
        resp = await self._request_with_retry("POST", "graphql", json=payload)

        data = resp.json()
        if data.get("message") == "ERROR_JSON_PAYLOAD_FORBIDDEN":
            raise GLPIAPIError(resp.status_code, data["message"], data)
        if resp.status_code >= 400:
            raise GLPIAPIError(
                resp.status_code, data.get("message", resp.reason_phrase), data
            )
        if "errors" in data:
            msg = data["errors"][0].get("message", "GraphQL query failed")
            raise GLPIAPIError(resp.status_code, msg, data)
        return data.get("data", data)


async def graphql_query_tool(params: GraphQLQueryParams) -> str:
    """Execute a GraphQL query and return JSON or an error message.

    This helper is used by automation agents when a quick GraphQL call is
    required without creating a long-lived client. According to the workflow
    described in ``AGENTS.md``, it can be combined with other tools to fetch
    ad-hoc data from GLPI.
    """

    client = GLPIClient(
        params.base_url,
        app_token=params.app_token,
        user_token=params.user_token,
        timeout=params.timeout,
        verify_ssl=params.verify_ssl,
        retry_max=params.retry_max,
        retry_base_delay=params.retry_base_delay,
    )
    try:
        await client.init_session()
        data = await client.query_graphql(params.query)
        return json.dumps(data)
    except Exception as exc:  # pragma: no cover - tool usage
        return str(exc)
    finally:
        await client.close()


__all__ = [
    "GLPIClient",
    "RestClientParams",
    "GraphQLQueryParams",
    "graphql_query_tool",
]
