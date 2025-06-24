"""Client for interacting with the GLPI REST API."""

from __future__ import annotations

import logging
import os
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv


STATUS = {1: "New", 2: "Processing", 3: "Assigned", 5: "Solved", 6: "Closed"}


class GLPIClient:
    """Lightweight GLPI API client.

    Parameters
    ----------
    base_url : str, optional
        Base URL for the API (``GLPI_URL`` env var by default).
    app_token : str, optional
        Application token (``GLPI_APP_TOKEN`` env var by default).
    user_token : str, optional
        User token (``GLPI_USER_TOKEN`` env var by default).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        app_token: Optional[str] = None,
        user_token: Optional[str] = None,
    ) -> None:
        load_dotenv()
        self.base_url = base_url or os.getenv("GLPI_URL")
        self.app_token = app_token or os.getenv("GLPI_APP_TOKEN")
        self.user_token = user_token or os.getenv("GLPI_USER_TOKEN")
        if not all([self.base_url, self.app_token, self.user_token]):
            raise ValueError("Missing GLPI credentials")
        self.session = requests.Session()
        self.session.headers.update({"App-Token": self.app_token})
        self.session_token: Optional[str] = None
        self.start_session()

    def start_session(self) -> None:
        """Initialize a session with the GLPI API."""
        resp = self.session.post(
            f"{self.base_url}/initSession",
            headers={"Authorization": f"user_token {self.user_token}"},
        )
        if resp.status_code >= 400:
            resp.raise_for_status()
        self.session_token = resp.json().get("session_token")
        if not self.session_token:
            raise RuntimeError("Failed to obtain session token")
        self.session.headers.update({"Session-Token": self.session_token})
        logging.debug("Started GLPI session %s", self.session_token)

    def kill_session(self) -> None:
        """Terminate the current session."""
        if not self.session_token:
            return
        resp = self.session.post(f"{self.base_url}/killSession")
        if resp.status_code >= 400:
            resp.raise_for_status()
        self.session.headers.pop("Session-Token", None)
        self.session_token = None
        logging.debug("Killed GLPI session")

    def _request(
        self, method: str, path: str, retry: bool = True, **kwargs
    ) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.request(method.upper(), url, **kwargs)
        if resp.status_code in {401, 403} and retry:
            logging.info("Session expired, restarting")
            self.start_session()
            resp = self.session.request(method.upper(), url, **kwargs)
        resp.raise_for_status()
        return resp

    def get(
        self, path: str, params: Optional[dict] = None
    ) -> requests.Response:
        """Perform a GET request."""
        return self._request("get", path, params=params)

    def post(
        self, path: str, json: Optional[dict] = None
    ) -> requests.Response:
        """Perform a POST request."""
        return self._request("post", path, json=json)

    def search(
        self,
        entity: str,
        criteria: Optional[Iterable[dict]] = None,
        forcedisplay_ids: Optional[List[int]] = None,
        range_: str = "0-999",
    ) -> List[dict]:
        """Search GLPI entities handling pagination."""

        start, end = [int(x) for x in range_.split("-")]
        step = end - start
        params: dict[str, object] = {}
        if criteria:
            for idx, c in enumerate(criteria):
                if "field" in c:
                    params[f"criteria[{idx}][field]"] = c["field"]
                    params[f"criteria[{idx}][searchtype]"] = c.get(
                        "searchtype", "contains"
                    )
                    params[f"criteria[{idx}][value]"] = c.get("value")
                if "link" in c:
                    params[f"criteria[{idx}][link]"] = c["link"]
        if forcedisplay_ids:
            for idx, fid in enumerate(forcedisplay_ids):
                params[f"forcedisplay[{idx}]"] = fid

        results: List[dict] = []
        while True:
            params["range"] = f"{start}-{end}"
            resp = self.get(f"search/{entity}", params=params)
            payload = resp.json()
            results.extend(payload.get("data", payload))
            content_range = resp.headers.get("Content-Range")
            if not content_range:
                break
            total = int(content_range.split("/")[-1])
            if end >= total - 1:
                break
            start = end + 1
            end = start + step
        return results
