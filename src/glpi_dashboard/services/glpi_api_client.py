from __future__ import annotations

"""Synchronous GLPI API client built on top of :class:`GLPISession`."""

from typing import Any, Dict, List, Optional
import asyncio
import logging
import requests

from .glpi_session import GLPISession, Credentials
from .exceptions import HTTP_STATUS_ERROR_MAP, GLPIAPIError

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


class GLPIAPIClient:
    """Simple synchronous wrapper around :class:`GLPISession`."""

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
    def __enter__(self) -> "GLPIAPIClient":
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
            self._loop.run_until_complete(self._session.__aexit__(exc_type, exc, tb))
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
            try:
                data = resp.json()
            except ValueError:
                data = {}
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
            else:
                exc_cls = HTTP_STATUS_ERROR_MAP.get(resp.status_code, GLPIAPIError)
                raise exc_cls(resp.status_code, data.get("message", resp.reason), data)

        if resp.status_code >= 400:
            try:
                data = resp.json()
            except ValueError:
                data = {}
            exc_cls = HTTP_STATUS_ERROR_MAP.get(resp.status_code, GLPIAPIError)
            raise exc_cls(resp.status_code, data.get("message", resp.reason), data)

        try:
            data = resp.json()
        except ValueError:
            data = {}
        return data, resp.headers

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_all(self, itemtype: str, **params: Any) -> List[Dict[str, Any]]:
        params = {**params, "expand_dropdowns": 1}
        endpoint = (
            f"search/{itemtype}" if not itemtype.startswith("search/") else itemtype
        )
        results: List[Dict[str, Any]] = []
        offset = 0
        while True:
            params["range"] = f"{offset}-{offset + 99}"
            data, headers = self._request_page(endpoint, params)
            page = data.get("data", data)
            if isinstance(page, dict):
                page = [page]
            for item in page:
                if isinstance(item, dict):
                    self._map_fields(item)
                    results.append(item)
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
        return results


class GlpiApiClient(GLPIAPIClient):
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
