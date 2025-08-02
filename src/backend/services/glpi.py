"""Service layer for interacting with the GLPI REST API.

This module encapsulates the logic required to fetch ticket information
from a GLPI instance using raw HTTP requests. The primary entry point
provided here is :func:`get_ticket_summary_by_group`, which aggregates
ticket counts by status for a fixed set of groups (service levels).

The implementation deliberately avoids any external GLPI SDKs in favour
of plain `requests` calls. Authentication is handled via the App Token
and Session Token provided by the environment. Should either token be
missing the calls will still be attempted, but the GLPI server is
expected to reject them, in which case the returned counts will be
empty and the error logged. This behaviour ensures that failures are
silent from the API consumer's perspective but visible in logs.

Environment variables expected:

- ``GLPI_BASE_URL`` – the root URL of the GLPI REST API (e.g. ``https://glpi.example.com/apirest.php``)
- ``GLPI_APP_TOKEN`` – the application token configured in GLPI
- ``GLPI_SESSION_TOKEN`` – the session token obtained from a prior login

If these variables are not defined, the defaults will be empty strings
which will still lead to a request being made (and likely a 401).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import requests

from backend.constants import GROUP_IDS

logger = logging.getLogger(__name__)

# Load configuration from environment once at import time. This avoids
# reading environment variables on every function call but still allows
# them to be overridden for tests via monkeypatch.
GLPI_BASE_URL: str = os.getenv("GLPI_BASE_URL", "").rstrip("/")
GLPI_APP_TOKEN: str = os.getenv("GLPI_APP_TOKEN", "")
GLPI_SESSION_TOKEN: str = os.getenv("GLPI_SESSION_TOKEN", "")


def _build_headers() -> Dict[str, str]:
    """Construct HTTP headers for GLPI requests.

    Returns:
        dict: A dictionary containing authentication headers required by GLPI.
    """
    return {
        "App-Token": GLPI_APP_TOKEN,
        "Session-Token": GLPI_SESSION_TOKEN,
        "Content-Type": "application/json",
    }


def get_ticket_summary_by_group() -> Dict[str, Dict[str, int]]:
    """Retrieve ticket counts grouped by status for each configured support level.

    For each service level defined in :data:`GROUP_IDS`, this function
    performs a search query against the GLPI REST API to list tickets
    belonging to that level's group. The results are aggregated into
    status buckets (e.g. ``"new"``, ``"assigned"``, ``"solved"``).

    Returns:
        dict: A nested mapping where the first key is the level name
        (``"N1"``, ``"N2"``, etc.) and the value is a dictionary
        mapping status names (lowercased) to integer counts.

    The function attempts to fail silently: any error while calling
    GLPI (network issues, HTTP errors, JSON decoding problems) will
    result in an empty dictionary for the affected level. Such errors
    are logged to aid troubleshooting.
    """
    summary: Dict[str, Dict[str, int]] = {}
    headers = _build_headers()
    # Base URL sanity check; early return if misconfigured
    if not GLPI_BASE_URL:
        logger.warning("GLPI_BASE_URL is not configured; returning empty summary")
        return {level: {} for level in GROUP_IDS.keys()}

    for level_name, group_id in GROUP_IDS.items():
        status_counts: Dict[str, int] = {}
        try:
            # Construct search parameters for filtering tickets by group ID. In
            # GLPI, the search endpoint is /search/<ItemType> and uses a
            # criteria array. Field 12 corresponds to the group associated
            # with the ticket. 'equals' ensures only tickets assigned to
            # the specified group are returned. forcedisplay controls the
            # fields included in the response.
            params = {
                "criteria[0][link]": "AND",
                "criteria[0][field]": "12",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(group_id),
                # Request id, status and group fields explicitly
                "forcedisplay[0]": "2",  # ticket id
                "forcedisplay[1]": "15",  # status
                "forcedisplay[2]": "12",  # group
            }
            url = f"{GLPI_BASE_URL}/search/Ticket"
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            try:
                data: Any = response.json()
            except ValueError:
                logger.exception(
                    "Failed to decode JSON from GLPI response for group %s", group_id
                )
                summary[level_name] = {}
                continue

            # The GLPI search API returns a dictionary with a 'data' key
            # containing a list of items. Some installations may return the
            # list directly; handle both.
            tickets = data.get("data") if isinstance(data, dict) else data
            if tickets is None:
                logger.warning(
                    "No 'data' field in GLPI response for group %s; raw response: %s",
                    group_id,
                    data,
                )
                summary[level_name] = {}
                continue
            for item in tickets:
                status_name = None
                # `item` is expected to be a dict with either a 'status' field
                # directly, or a nested object with a 'name'. Attempt both.
                if isinstance(item, dict):
                    # Top-level status string or numeric code
                    if "status" in item and not isinstance(item["status"], dict):
                        status_name = str(item.get("status")).lower()
                    # Sometimes GLPI includes a more descriptive field
                    if not status_name and item.get("status_name"):
                        status_name = str(item.get("status_name"))
                    # Nested dict case: status: { id: int, name: str }
                    if status_name is None and isinstance(item.get("status"), dict):
                        status_name = str(item["status"].get("name")).lower()
                if not status_name:
                    # Skip items without a valid status
                    continue
                status_counts[status_name] = status_counts.get(status_name, 0) + 1
            summary[level_name] = status_counts
        except Exception:
            logger.exception("Error while fetching tickets for group ID %s", group_id)
            summary[level_name] = {}
    return summary
