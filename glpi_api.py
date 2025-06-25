"""Simplified GLPI API helper."""

from __future__ import annotations

import os
from typing import Iterable, List, Optional

import requests
from dotenv import load_dotenv
from requests import Session


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
    app_token = os.getenv("GLPI_APP_TOKEN")
    user_token = os.getenv("GLPI_USER_TOKEN")
    if not all([url, app_token, user_token]):
        raise ValueError("Missing GLPI environment variables")

    session = requests.Session()
    resp = session.get(
        f"{url}/initSession",
        headers={
            "App-Token": app_token,
            "Authorization": f"user_token {user_token}",
        },
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
    status: Optional[str] = None,
    limit: int = 100,
    criteria: Iterable[dict] | None = None,
    session: Optional[Session] = None,
) -> List[dict]:
    """Retrieve tickets via ``/search/Ticket`` endpoint.

    Parameters
    ----------
    status : str, optional
        Status filter added as a search criterion.
    limit : int, optional
        Maximum number of results.
    criteria : Iterable[dict], optional
        Additional GLPI search criteria.
    session : Session, optional
        Existing session; created when ``None``.

    Returns
    -------
    list[dict]
        Ticket objects returned by the API.
    """
    load_dotenv()
    url = os.getenv("GLPI_URL")
    if session is None:
        session = login()

    params: dict[str, object] = {"range": f"0-{limit - 1}"}
    all_criteria = list(criteria or [])
    if status is not None:
        all_criteria.append(
            {"field": "status", "searchtype": "equals", "value": status}
        )

    for idx, crit in enumerate(all_criteria):
        params[f"criteria[{idx}][field]"] = crit["field"]
        params[f"criteria[{idx}][searchtype]"] = crit.get(
            "searchtype",
            "equals",
        )
        params[f"criteria[{idx}][value]"] = crit["value"]

    resp = session.get(f"{url}/search/Ticket", params=params)
    resp.raise_for_status()
    data = resp.json()
    return list(data.get("data", data))


def create_ticket(data: dict, session: Session | None = None) -> dict:
    """Create a ticket using ``POST /Ticket``."""
    load_dotenv()
    url = os.getenv("GLPI_URL")
    if session is None:
        session = login()
    resp = session.post(f"{url}/Ticket", json=data)
    resp.raise_for_status()
    return dict(resp.json())


def update_ticket(
    ticket_id: int,
    data: dict,
    session: Session | None = None,
) -> dict:
    """Update a ticket using ``PUT /Ticket/<id>``."""
    load_dotenv()
    url = os.getenv("GLPI_URL")
    if session is None:
        session = login()
    resp = session.put(f"{url}/Ticket/{ticket_id}", json=data)
    resp.raise_for_status()
    return dict(resp.json())
