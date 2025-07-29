from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

pytest.importorskip("py_glpi")

from glpi_sdk import count_by_levels  # noqa: E402


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
