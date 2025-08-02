"""Tests for the GLPI ticket summary service.

These tests exercise the high‑level behaviour of the service function
``get_ticket_summary_by_group`` by stubbing out network calls to
``requests.get``.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

import backend.services.glpi as glpi_service


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


def test_get_ticket_summary_handles_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """When GLPI requests time out, the service should return empty counts."""

    def _timeout_get(*args, **kwargs):  # pragma: no cover - simple helper
        raise glpi_service.requests.exceptions.Timeout()

    monkeypatch.setattr(glpi_service.requests, "get", _timeout_get)
    monkeypatch.setattr(glpi_service, "GLPI_BASE_URL", "http://test")

    summary = glpi_service.get_ticket_summary_by_group()

    expected: Dict[str, Dict[str, int]] = {
        level: {} for level in glpi_service.GROUP_IDS.keys()
    }
    assert summary == expected
