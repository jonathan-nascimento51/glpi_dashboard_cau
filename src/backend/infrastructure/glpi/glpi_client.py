from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

import requests

from shared.utils.resilience import call_with_breaker, retry_api_call

from .glpi_client_logging import (
    bind_request,
    clear_request,
    get_logger,
)

logger = get_logger(__name__)


class GLPIClientError(Exception):
    """Base exception for GLPI client failures."""


class GLPIClientAuthError(GLPIClientError):
    """Authentication failed or session expired."""


class GLPIClientNotFound(GLPIClientError):
    """Requested resource does not exist."""


class GLPIClientRateLimit(GLPIClientError):
    """Too many requests."""


class GLPIClientServerError(GLPIClientError):
    """Generic server side error."""


HTTP_ERROR_MAP = {
    400: GLPIClientError,
    401: GLPIClientAuthError,
    403: GLPIClientAuthError,
    404: GLPIClientNotFound,
    429: GLPIClientRateLimit,
}


def get_secret(name: str) -> str:
    """Return secret value from env or ``*_FILE`` path."""

    file_var = os.getenv(f"{name}_FILE")
    if file_var:
        try:
            with open(file_var, "r", encoding="utf-8") as fh:
                return fh.read().strip()
        except OSError as exc:  # pragma: no cover - file errors
            raise RuntimeError(f"unable to read secret file for {name}") from exc
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"secret {name} not found")


class GLPISessionManager:
    """Synchronous session manager for the GLPI REST API."""

    def __init__(
        self,
        base_url: str,
        app_token: str,
        *,
        user_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify: bool = True,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.user_token = user_token
        self.username = username
        self.password = password
        self.verify = verify
        self.session = session or requests.Session()
        self.session_token: Optional[str] = None

    def __enter__(self) -> "GLPISessionManager":
        self._open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------
    @call_with_breaker
    @retry_api_call
    def _open(self) -> None:
        headers = {"App-Token": self.app_token, "Content-Type": "application/json"}
        auth = None
        if self.user_token:
            headers["Authorization"] = f"user_token {self.user_token}"
        elif self.username and self.password:
            auth = (self.username, self.password)
        resp = self.session.get(
            f"{self.base_url}/initSession",
            headers=headers,
            auth=auth,
            verify=self.verify,
        )
        self._handle_response(resp)
        data = resp.json()
        self.session_token = data.get("session_token")
        logger.info("session opened")

    @call_with_breaker
    @retry_api_call
    def _kill(self) -> None:
        if not self.session_token:
            return
        headers = {
            "App-Token": self.app_token,
            "Session-Token": self.session_token,
            "Content-Type": "application/json",
        }
        resp = self.session.get(
            f"{self.base_url}/killSession", headers=headers, verify=self.verify
        )
        self._handle_response(resp, raise_for_status=False)
        logger.info("session closed")
        self.session_token = None

    def close(self) -> None:
        self._kill()
        self.session.close()

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------
    @call_with_breaker
    @retry_api_call
    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        headers = kwargs.pop("headers", {})
        headers.setdefault("App-Token", self.app_token)
        if self.session_token:
            headers.setdefault("Session-Token", self.session_token)
        headers.setdefault("Content-Type", "application/json")
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_id = uuid.uuid4().hex
        bind_request(request_id=request_id, method=method, url=url)
        log = logger.bind(request_id=request_id, method=method, url=url)

        try:
            resp = self.session.request(
                method, url, headers=headers, verify=self.verify, **kwargs
            )
            self._handle_response(resp)
            content_type = resp.headers.get("Content-Type", "").lower()
            log.debug("request completed", status=resp.status_code)
            if content_type.startswith("application/json"):
                return resp.json()
            return resp.text
        finally:
            clear_request()

    def _handle_response(
        self, resp: requests.Response, *, raise_for_status: bool = True
    ) -> None:
        if resp.status_code >= 400:
            exc_cls = HTTP_ERROR_MAP.get(resp.status_code, GLPIClientServerError)
            raise exc_cls(f"HTTP {resp.status_code}: {resp.text}")
        if raise_for_status:
            resp.raise_for_status()

    # ------------------------------------------------------------------
    # High level API
    # ------------------------------------------------------------------
    def get_item(self, itemtype: str, item_id: int) -> Any:
        return self._make_request("GET", f"{itemtype}/{item_id}")

    def get_all_items(self, itemtype: str) -> Any:
        return self._make_request("GET", itemtype)

    def get_sub_items(self, itemtype: str, item_id: int, sub_type: str) -> Any:
        return self._make_request("GET", f"{itemtype}/{item_id}/{sub_type}")

    def add_item(self, itemtype: str, payload: Dict[str, Any]) -> Any:
        return self._make_request("POST", itemtype, json=payload)

    def update_item(self, itemtype: str, item_id: int, payload: Dict[str, Any]) -> Any:
        return self._make_request("PUT", f"{itemtype}/{item_id}", json=payload)

    def search(self, itemtype: str, criteria: "SearchCriteriaBuilder") -> Any:
        params = criteria.build()
        return self._make_request("GET", f"search/{itemtype}", params=params)

    def search_by_date_range(
        self,
        itemtype: str,
        field: str,
        start: str,
        end: str,
    ) -> Any:
        builder = SearchCriteriaBuilder().between(field, start, end)
        return self.search(itemtype, builder)


class SearchCriteriaBuilder:
    """Helper to compose GLPI search criteria."""

    def __init__(self) -> None:
        self._criteria: list[dict[str, Any]] = []

    def add(
        self,
        field: str,
        value: str,
        *,
        searchtype: str = "contains",
        link: str = "AND",
    ) -> "SearchCriteriaBuilder":
        self._criteria.append(
            {
                "field": field,
                "searchtype": searchtype,
                "value": value,
                "link": link,
            }
        )
        return self

    def between(self, field: str, start: str, end: str) -> "SearchCriteriaBuilder":
        self._criteria.append(
            {
                "field": field,
                "searchtype": "between",
                "value": f"{start}|{end}",
                "link": "AND",
            }
        )
        return self

    def build(self) -> Dict[str, str]:
        params: Dict[str, str] = {}
        for idx, crit in enumerate(self._criteria):
            for key, value in crit.items():
                params[f"criteria[{idx}][{key}]"] = str(value)
        return params


__all__ = [
    "GLPISessionManager",
    "GLPIClientError",
    "GLPIClientAuthError",
    "GLPIClientNotFound",
    "GLPIClientRateLimit",
    "GLPIClientServerError",
    "SearchCriteriaBuilder",
    "get_secret",
]
