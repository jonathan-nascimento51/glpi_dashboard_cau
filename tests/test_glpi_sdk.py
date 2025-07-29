from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from glpi_sdk import count_by_levels  # noqa: E402

# Dynamically import ``GLPISDK`` from the infrastructure module without loading
# its heavy package dependencies.
SDK_PATH = Path("src/backend/infrastructure/glpi/glpi_sdk.py")

if "py_glpi.resources.users" not in sys.modules:
    stub = types.ModuleType("py_glpi.resources.users")
    stub.Users = MagicMock  # type: ignore[attr-defined]
    sys.modules["py_glpi.resources.users"] = stub

spec = importlib.util.spec_from_file_location("glpi_sdk_impl", SDK_PATH)
assert spec is not None
glpi_sdk_impl = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(glpi_sdk_impl)

GLPISDK = glpi_sdk_impl.GLPISDK
ResourceNotFound = glpi_sdk_impl.ResourceNotFound


@pytest.fixture()
def fake_session():
    return MagicMock(name="GLPISession")


def test_count_by_levels_calls_tickets_count(fake_session):
    levels = ["N1", "N2"]
    ticket_mock = MagicMock()
    ticket_mock.count.side_effect = [1, 2, 3, 4, 5, 6]

    with patch("glpi_sdk.Tickets", return_value=ticket_mock) as tickets_cls:
        result = count_by_levels(fake_session, levels)

    tickets_cls.assert_called_once_with(fake_session)
    expected_calls = [
        call(
            criteria=[
                {"field": "groups_id_assign", "searchtype": "equals", "value": "N1"},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": 1},
            ]
        ),
        call(
            criteria=[
                {"field": "groups_id_assign", "searchtype": "equals", "value": "N1"},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": 4},
            ]
        ),
        call(
            criteria=[
                {"field": "groups_id_assign", "searchtype": "equals", "value": "N1"},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": 5},
            ]
        ),
        call(
            criteria=[
                {"field": "groups_id_assign", "searchtype": "equals", "value": "N2"},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": 1},
            ]
        ),
        call(
            criteria=[
                {"field": "groups_id_assign", "searchtype": "equals", "value": "N2"},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": 4},
            ]
        ),
        call(
            criteria=[
                {"field": "groups_id_assign", "searchtype": "equals", "value": "N2"},
                {"link": "AND"},
                {"field": "status", "searchtype": "equals", "value": 5},
            ]
        ),
    ]
    ticket_mock.count.assert_has_calls(expected_calls)

    assert result == {
        "N1": {"new": 1, "pending": 2, "solved": 3},
        "N2": {"new": 4, "pending": 5, "solved": 6},
    }


def test_get_ticket_counts_by_level_empty_levels(monkeypatch: pytest.MonkeyPatch):
    """Returns empty dict if levels is empty."""
    monkeypatch.setattr(glpi_sdk_impl, "GLPISession", MagicMock())
    sdk = GLPISDK("http://example.com", "APP")
    sdk.list_tickets_by_level = MagicMock()
    result = sdk.get_ticket_counts_by_level("lvl", {})
    assert result == {}


def test_get_ticket_counts_by_level_empty_tickets(monkeypatch: pytest.MonkeyPatch):
    """Returns all status counts as 0 if list_tickets_by_level returns empty list."""
    monkeypatch.setattr(glpi_sdk_impl, "GLPISession", MagicMock())
    sdk = GLPISDK("http://example.example.com", "APP")
    sdk.list_tickets_by_level = MagicMock(return_value=[])
    result = sdk.get_ticket_counts_by_level("lvl", {"A": 10})
    assert result == {
        "A": {"new": 0, "processing": 0, "waiting": 0, "solved": 0, "closed": 0},
    }


def test_list_tickets_by_level_handles_not_found(monkeypatch: pytest.MonkeyPatch):
    """``list_tickets_by_level`` returns an empty list on ``ResourceNotFound``."""

    tickets_mock = MagicMock()
    tickets_mock.search.side_effect = ResourceNotFound("nope")

    monkeypatch.setattr(glpi_sdk_impl, "Tickets", lambda *_: tickets_mock)
    monkeypatch.setattr(glpi_sdk_impl, "GLPISession", MagicMock())

    sdk = GLPISDK("http://example.com", "APP")
    result = sdk.list_tickets_by_level("groups_id", 1)

    assert result == []
    tickets_mock.search.assert_called_once()


def test_get_ticket_priority_and_requester(monkeypatch: pytest.MonkeyPatch):
    """Priority label and requester name are retrieved correctly."""

    ticket = MagicMock(priority_string="High", users_id_recipient=42)
    tickets_mock = MagicMock(get=MagicMock(return_value=ticket))
    user = MagicMock()
    user.name = "Bob"
    users_mock = MagicMock(get=MagicMock(return_value=user))

    monkeypatch.setattr(glpi_sdk_impl, "Tickets", lambda *_: tickets_mock)
    monkeypatch.setattr(glpi_sdk_impl, "Users", lambda *_: users_mock)
    monkeypatch.setattr(glpi_sdk_impl, "GLPISession", MagicMock())

    sdk = GLPISDK("http://example.com", "APP")
    data = sdk.get_ticket_priority_and_requester(7)

    tickets_mock.get.assert_called_once_with(7)
    users_mock.get.assert_called_once_with(42)
    assert data == {"priority": "High", "requester": "Bob"}


def test_get_ticket_counts_by_level(monkeypatch: pytest.MonkeyPatch):
    """Statuses are aggregated per level using ``list_tickets_by_level``."""

    level_a = [MagicMock(status=1), MagicMock(status=4)]
    level_b = [MagicMock(status=4), MagicMock(status=4), MagicMock(status=5)]

    monkeypatch.setattr(glpi_sdk_impl, "GLPISession", MagicMock())
    sdk = GLPISDK("http://example.com", "APP")
    sdk.list_tickets_by_level = MagicMock(side_effect=[level_a, level_b])

    result = sdk.get_ticket_counts_by_level("lvl", {"A": 10, "B": 20})

    sdk.list_tickets_by_level.assert_has_calls([call("lvl", 10), call("lvl", 20)])
    assert result == {
        "A": {"new": 1, "processing": 0, "waiting": 0, "solved": 1, "closed": 0},
        "B": {"new": 0, "processing": 0, "waiting": 0, "solved": 2, "closed": 1},
    }
