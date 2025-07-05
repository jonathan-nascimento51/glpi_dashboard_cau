# mypy: ignore-errors
# ruff: noqa: E402
from __future__ import annotations

"""Synchronous GLPI API client built on top of :class:`GLPISession`."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from pydantic import BaseModel, Field

from .exceptions import HTTP_STATUS_ERROR_MAP, GLPIAPIError
from .glpi_session import Credentials, GLPISession

logger = logging.getLogger(__name__)

STATUS_MAP = {
    1: "New",
    2: "Processing (assigned)",
    3: "Processing (planned)",
    4: "Waiting",
    5: "Solved",
    6: "Closed",
}

PRIORITY_MAP = {1: "Very Low", 2: "Low", 3: "Medium", 4: "High", 5: "Very High"}
IMPACT_MAP = {1: "None", 2: "Low", 3: "Medium", 4: "High"}
TYPE_MAP = {1: "Incident", 2: "Request"}


class ApiClientParams(BaseModel):
    """Input data for :class:`GlpiApiClient` construction."""

    base_url: str = Field(..., description="GLPI REST base URL")
    credentials: Credentials
    session_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Extra parameters forwarded to session"
    )


class GlpiApiClient:
    """Simple synchronous wrapper around :class:`GLPISession`.

    This tool is convenient for scripts or CLI utilities that cannot run
    asynchronous code. It manages the event loop internally and exposes
    blocking methods for interacting with the GLPI API.
    """

    def __init__(
        self,
        base_url: str,
        credentials: Credentials,
        **session_kwargs: Any,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.credentials = credentials
        self.session_kwargs = session_kwargs
        self._session: Optional[GLPISession] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ------------------------------------------------------------------
    # Context manager helpers
    # ------------------------------------------------------------------
    def __enter__(self) -> "GlpiApiClient":
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._session = GLPISession(
            self.base_url,
            self.credentials,
            **self.session_kwargs,
        )
        self._loop.run_until_complete(self._session.__aenter__())
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._session is not None and self._loop is not None:
            if hasattr(self._session, "close"):
                self._loop.run_until_complete(self._session.close())
            self._loop.close()
            self._session = None
            self._loop = None

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _map_fields(self, item: Dict[str, Any]) -> None:
        for field, mapping in (
            ("status", STATUS_MAP),
            ("priority", PRIORITY_MAP),
            ("impact", IMPACT_MAP),
            ("type", TYPE_MAP),
        ):
            value = item.get(field)
            try:
                num = int(value)
            except (TypeError, ValueError):
                continue
            item[field] = mapping.get(num, value)

    def _map_fields_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vectorized version of ``_map_fields`` for multiple items."""
        if not items:
            return items
        df = pd.DataFrame(items)
        for field, mapping in (
            ("status", STATUS_MAP),
            ("priority", PRIORITY_MAP),
            ("impact", IMPACT_MAP),
            ("type", TYPE_MAP),
        ):
            if field in df.columns:
                df[field] = (
                    pd.to_numeric(df[field], errors="coerce")
                    .map(mapping)
                    .fillna(df[field])
                )
        return df.to_dict(orient="records")

    def _flatten_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Expand list values into ``key[index]`` query parameters."""

        flat: Dict[str, Any] = {}
        for key, value in params.items():
            if isinstance(value, list):
                for idx, val in enumerate(value):
                    flat[f"{key}[{idx}]"] = val
            else:
                flat[key] = value
        return flat

    def _parse_json(self, resp: requests.Response) -> Dict[str, Any]:
        """Return JSON content or an empty dict if decoding fails."""
        try:
            return resp.json()
        except ValueError:
            return {}

    def _raise_error(self, resp: requests.Response, data: Dict[str, Any]) -> None:
        """Raise an exception mapped from the HTTP status code."""
        exc_cls = HTTP_STATUS_ERROR_MAP.get(resp.status_code, GLPIAPIError)
        raise exc_cls(resp.status_code, data.get("message", resp.reason), data)

    def _request_page(
        self, endpoint: str, params: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, str]]:
        if self._session is None:
            raise RuntimeError("Client session not started")

        headers = {
            "App-Token": self.credentials.app_token,
            "Session-Token": self._session._session_token or "",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30,
            verify=self._session.verify_ssl,
            proxies=(
                {
                    "http": self._session.proxy,
                    "https": self._session.proxy,
                }
                if self._session.proxy
                else None
            ),
        )
        if resp.status_code == 401:
            data = self._parse_json(resp)
            if data.get("message") == "ERROR_SESSION_TOKEN_INVALID":
                logger.warning("Session token invalid, refreshing and retrying")
                self._loop.run_until_complete(self._session._refresh_session_token())
                headers["Session-Token"] = self._session._session_token or ""
                resp = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30,
                    verify=self._session.verify_ssl,
                    proxies=(
                        {
                            "http": self._session.proxy,
                            "https": self._session.proxy,
                        }
                        if self._session.proxy
                        else None
                    ),
                )
                data = self._parse_json(resp)
            else:
                self._raise_error(resp, data)
        elif resp.status_code >= 400:
            data = self._parse_json(resp)
            self._raise_error(resp, data)
        else:
            data = self._parse_json(resp)
        return data, resp.headers

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_all(self, itemtype: str, **params: Any) -> List[Dict[str, Any]]:
        params = {**params, "expand_dropdowns": 1}
        endpoint = itemtype if itemtype.startswith("search/") else f"search/{itemtype}"
        results: List[Dict[str, Any]] = []
        offset = 0
        while True:
            params["range"] = f"{offset}-{offset + 99}"
            data, headers = self._request_page(endpoint, params)
            page = data.get("data", data)
            if isinstance(page, dict):
                page = [page]
            page_items = [item for item in page if isinstance(item, dict)]
            results.extend(page_items)
            content_range = headers.get("Content-Range")
            if not content_range:
                break
            try:
                total = int(content_range.split("/")[1])
            except (IndexError, ValueError):
                break
            offset += 100
            if offset >= total:
                break
        return self._map_fields_batch(results)

    def search(
        self, itemtype: str, criteria: List[Dict[str, Any]], **params: Any
    ) -> List[Dict[str, Any]]:
        """Search for items using GLPI search criteria.

        Parameters
        ----------
        itemtype:
            The GLPI item type (e.g. ``Ticket``).
        criteria:
            A list of dictionaries representing GLPI search criteria.
            Each dictionary should contain keys like ``field``, ``searchtype``
            and ``value``.
        params:
            Additional query parameters to include in the request.
        """

        search_params: Dict[str, Any] = {}
        for k, v in params.items():
            if isinstance(v, list):
                for idx, val in enumerate(v):
                    search_params[f"{k}[{idx}]"] = val
            else:
                search_params[k] = v

        for idx, cond in enumerate(criteria):
            for key, value in cond.items():
                search_params[f"criteria[{idx}][{key}]"] = value

        return self.get_all(f"search/{itemtype}", **search_params)


class TokenGlpiApiClient(GlpiApiClient):
    """Convenience wrapper using tokens directly."""

    def __init__(
        self,
        base_url: str,
        app_token: str,
        user_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **session_kwargs: Any,
    ) -> None:
        creds = Credentials(
            app_token=app_token,
            user_token=user_token,
            username=username,
            password=password,
        )
        super().__init__(base_url, creds, **session_kwargs)

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if self._session is None or self._loop is None:
            raise RuntimeError("Client session not started")
        return self._loop.run_until_complete(self._session.get(endpoint, params=params))


# Backwards compatibility
GLPIAPIClient = GlpiApiClient


def fetch_tickets_tool(params: ApiClientParams) -> str:
    """Fetch all tickets using the synchronous client.

    This wrapper is intended for CLI utilities or agents that cannot run
    asynchronous code.  It fits the tooling approach described in
    ``AGENTS.md`` where discrete functions return JSON or error strings for
    further processing.
    """

    try:
        client = GlpiApiClient(
            params.base_url, params.credentials, **params.session_kwargs
        )
        with client as sess:
            data = sess.get_all("Ticket")
        return json.dumps(data)
    except Exception as exc:  # pragma: no cover - tool usage
        return str(exc)


__all__ = [
    "GlpiApiClient",
    "TokenGlpiApiClient",
    "ApiClientParams",
    "fetch_tickets_tool",
]
