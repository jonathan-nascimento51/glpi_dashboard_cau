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

import base64
import logging
from typing import Any, Dict, Optional

import httpx

from .exceptions import GLPIAPIError

logger = logging.getLogger(__name__)


class GLPIClient:
    """Asynchronous client for the GLPI REST API."""

    def __init__(
        self,
        base_url: str,
        app_token: str,
        user_token: Optional[str] = None,
        *,
        timeout: float = 30.0,
        verify_ssl: bool = True,
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
        """

        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.user_token = user_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
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
        try:
            resp = await self._client.get(url, params=params)
        except httpx.TimeoutException as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"Timeout during search: {exc}") from exc
        except httpx.HTTPError as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"HTTP error during search: {exc}") from exc

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
        try:
            resp = await self._client.get(url)
        except httpx.TimeoutException as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"Timeout during listSearchOptions: {exc}") from exc
        except httpx.HTTPError as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(
                0, f"HTTP error during listSearchOptions: {exc}"
            ) from exc

        data = resp.json()
        if data.get("message") == "ERROR_JSON_PAYLOAD_FORBIDDEN":
            raise GLPIAPIError(resp.status_code, data["message"], data)
        if resp.status_code >= 400:
            raise GLPIAPIError(
                resp.status_code, data.get("message", resp.reason_phrase), data
            )
        return data

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
        try:
            resp = await self._client.post("graphql", json=payload)
        except httpx.TimeoutException as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"Timeout during GraphQL query: {exc}") from exc
        except httpx.HTTPError as exc:  # pragma: no cover - network issues
            raise GLPIAPIError(0, f"HTTP error during GraphQL query: {exc}") from exc

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


__all__ = ["GLPIClient"]
