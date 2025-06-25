from __future__ import annotations

"""GLPI REST API client with basic search support."""

import logging
import os
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv
from requests import Session


log = logging.getLogger(__name__)


class GLPIClient:
    """Wrapper around the GLPI REST API."""

    def __init__(self) -> None:
        load_dotenv()
        self.base_url = os.getenv("GLPI_URL")
        self.app_token = os.getenv("APP_TOKEN")
        self.user_token = os.getenv("USER_TOKEN")
        if not all([self.base_url, self.app_token, self.user_token]):
            raise ValueError("Missing GLPI environment variables")
        self.session = Session()
        self.session_token: Optional[str] = None

    # ------------------------------------------------------------------
    def start_session(self) -> None:
        """Start a GLPI session via ``POST /initSession``."""
        log.debug("Starting session")
        resp = self.session.post(
            f"{self.base_url}/initSession",
            headers={
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}",
            },
        )
        if resp.status_code in (401, 403):
            raise requests.HTTPError("Unauthorized", response=resp)
        resp.raise_for_status()
        self.session_token = resp.json().get("session_token")
        self.session.headers.update(
            {
                "Session-Token": self.session_token,
                "App-Token": self.app_token,
                "Authorization": f"user_token {self.user_token}",
            }
        )

    # ------------------------------------------------------------------
    def kill_session(self) -> None:
        """Close the current session."""
        if not self.session_token:
            return
        resp = self.session.post(f"{self.base_url}/killSession")
        resp.raise_for_status()
        self.session_token = None
        self.session.headers.pop("Session-Token", None)

    # ------------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/') }"
        resp = self.session.request(method, url, **kwargs)
        if resp.status_code in (401, 403):
            log.info("Session expired, restarting")
            self.start_session()
            resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        """GET request helper."""
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict | None = None) -> requests.Response:
        """POST request helper."""
        return self._request("POST", path, json=json)

    # ------------------------------------------------------------------
    def search(
        self,
        entity: str,
        criteria: Iterable[dict] | None = None,
        forcedisplay_ids: Iterable[int] | None = None,
        range_: str = "0-999",
    ) -> List[dict]:
        """Search for an entity handling pagination."""
        if not self.session_token:
            self.start_session()
        params: dict[str, object] = {"range": range_}
        if criteria:
            for i, crit in enumerate(criteria):
                for key, value in crit.items():
                    if key == "link":
                        params[f"criteria[{i}][link]"] = value
                    else:
                        params[f"criteria[{i}][{key}]"] = value
        if forcedisplay_ids:
            for i, fid in enumerate(forcedisplay_ids):
                params[f"forcedisplay[{i}]"] = fid

        results: List[dict] = []
        start, end = [int(x) for x in params["range"].split("-")]
        step = end - start
        while True:
            resp = self.get(f"search/{entity}", params=params)
            data = resp.json().get("data", [])
            results.extend(data)
            crange = resp.headers.get("Content-Range")
            if not crange:
                break
            _range, total = crange.split("/")
            _, last = _range.split("-")
            last = int(last)
            total = int(total)
            if last + 1 >= total:
                break
            start = last + 1
            end = start + step
            params["range"] = f"{start}-{end}"
        return results
