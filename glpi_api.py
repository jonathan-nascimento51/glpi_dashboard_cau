"""Simplified GLPI API helper."""

from __future__ import annotations

import os
from typing import List, Optional

import requests
from requests import Session
from dotenv import load_dotenv


class UnauthorizedError(requests.HTTPError):
    """Raised when login fails due to invalid credentials."""


def login() -> Session:
    """Create an authenticated session using environment variables.

    Returns
    -------
    requests.Session
        Session with authentication headers set.
    """
    load_dotenv()
    url = os.getenv("GLPI_URL")
    app_token = os.getenv("APP_TOKEN")
    user_token = os.getenv("USER_TOKEN")
    if not all([url, app_token, user_token]):
        raise ValueError("Missing GLPI environment variables")

    session = requests.Session()
    resp = session.get(
        f"{url}/initSession",
        headers={"App-Token": app_token, "Authorization": f"user_token {user_token}"},
    )
    if resp.status_code == 401:
        raise UnauthorizedError("Invalid tokens", response=resp)
    resp.raise_for_status()
    token = resp.json().get("session_token")
    session.headers.update(
        {
            "Session-Token": token,
            "App-Token": app_token,
            "Authorization": f"user_token {user_token}",
        }
    )
    return session


def get_tickets(
    status: Optional[str] = None, limit: int = 100, session: Optional[Session] = None
) -> List[dict]:
    """Retrieve tickets from GLPI.

    Parameters
    ----------
    status : str, optional
        Filter by status, by default ``None``.
    limit : int, optional
        Maximum number of tickets, by default ``100``.
    session : Session, optional
        Existing session; if ``None`` a new one is created.

    Returns
    -------
    List[dict]
        Ticket objects from the API.
    """
    load_dotenv()
    url = os.getenv("GLPI_URL")
    if session is None:
        session = login()

    params = {"limit": limit}
    if status is not None:
        params["status"] = status
    resp = session.get(f"{url}/tickets", params=params)
    resp.raise_for_status()
    return list(resp.json())