"""Tests for the GLPI ticket summary service and API route.

These tests exercise the high‑level behaviour of the service function
``get_ticket_summary_by_group`` by stubbing out network calls to
``requests.get``. They also verify that the FastAPI route returns the
expected JSON structure when integrated into a minimal application.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

import backend.services.glpi as glpi_service
from backend.app import create_app


class FakeResponse:
    """Simple stand‑in for ``requests.Response`` used in tests."""

    def __init__(self, data: Any):
        self._data = data

    def raise_for_status(self) -> None:
        # No‑op: raising no error for successful responses
        return None

    def json(self) -> Any:
        return self._data


def _make_fake_get(responses: Dict[str, List[Dict[str, Any]]]):
    """Create a fake ``requests.get`` that returns canned data per group id.

    Args:
        responses: Mapping from group id string to a list of ticket dicts

    Returns:
        Callable matching the signature of ``requests.get``.
    """

    def _fake_get(
        url: str, headers: Dict[str, str], params: Dict[str, Any], timeout: int = 30
    ) -> FakeResponse:
        group_id = params.get("criteria[0][value]")
        data = responses.get(str(group_id), [])
        return FakeResponse({"data": data})

    return _fake_get


def test_get_ticket_summary_by_group(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that the service correctly aggregates status counts."""
    # Define canned responses for each group. Keys must be strings
    fake_data: Dict[str, List[Dict[str, Any]]] = {
        "89": [
            {"status": "new"},
            {"status": "new"},
            {"status": "assigned"},
        ],
        "90": [
            {"status": {"name": "solved"}},
            {"status": {"name": "solved"}},
            {"status": {"name": "new"}},
        ],
        "91": [],
        "92": [
            {"status": "new"},
        ],
    }
    monkeypatch.setattr(glpi_service.requests, "get", _make_fake_get(fake_data))
    monkeypatch.setattr(glpi_service, "GLPI_BASE_URL", "http://test")
    summary = glpi_service.get_ticket_summary_by_group()
    assert summary["N1"] == {"new": 2, "assigned": 1}
    assert summary["N2"] == {"solved": 2, "new": 1}
    assert summary["N3"] == {}
    assert summary["N4"] == {"new": 1}


def test_api_route_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure that the API route returns the service output verbatim."""
    # Prepare a simple deterministic summary to be returned by the service
    fake_summary = {"N1": {"new": 1}, "N2": {}, "N3": {}, "N4": {"assigned": 3}}
    monkeypatch.setattr(
        glpi_service, "get_ticket_summary_by_group", lambda: fake_summary
    )
    # Patch the reference imported in the route module as well
    from backend import routes as backend_routes

    monkeypatch.setattr(
        backend_routes.tickets, "get_ticket_summary_by_group", lambda: fake_summary
    )
    app = create_app()
    client = TestClient(app)
    response = client.get("/v1/metrics/levels")
    assert response.status_code == 200
    assert response.json() == fake_summary
