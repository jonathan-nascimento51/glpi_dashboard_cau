from typing import Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.glpi_api_client import (
    GlpiApiClient,
)
from backend.constants import GROUP_IDS
from backend.schemas.ticket_models import TEXT_STATUS_MAP


@pytest.mark.asyncio
async def test_populate_forced_fields(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
        lambda *a, **k: MagicMock(),
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.TicketTranslator",
        lambda *a, **k: MagicMock(),
    )
    session.list_search_options = AsyncMock(
        return_value={
            "1": {"field": "id"},
            "2": {"field": "name"},
            "3": {"field": "date"},
            "4": {"field": "priority"},
            "5": {"field": "status"},
            "6": {"field": "users_id_assign"},
        }
    )

    client = GlpiApiClient(session=session)
    await client._populate_forced_fields()

    assert client._forced_fields == [1, 2, 3, 4, 5, 6]
    session.list_search_options.assert_awaited_once_with("Ticket")


@pytest.mark.asyncio
async def test_resolve_ticket_fields(monkeypatch):
    session = MagicMock()
    mapper = MagicMock()
    mapper.get_search_options = AsyncMock(
        return_value={
            "10": {"field": "id"},
            "11": {"field": "name"},
            "12": {"field": "date_creation"},
            "13": {"field": "priority"},
            "14": {"field": "users_id_assign"},
        }
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService", lambda *a, **k: mapper
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.TicketTranslator",
        lambda *a, **k: MagicMock(),
    )

    client = GlpiApiClient(session=session)
    client._forced_fields = []
    await client._resolve_ticket_fields()

    assert client._forced_fields == [10, 11, 12, 13, 14]
    mapper.get_search_options.assert_awaited_once_with("Ticket")


@pytest.mark.asyncio
async def test_get_all_paginated_maps_fields(monkeypatch):
    session = MagicMock()
    session.list_search_options = AsyncMock(
        return_value={"1": {"field": "id"}, "2": {"field": "name"}}
    )

    pages: list[tuple[dict, dict]] = [
        ({"data": [{"1": 1, "2": "a"}, {"1": 2, "2": "b"}]}, {}),
        ({"data": [{"1": 3, "2": "c"}]}, {}),
        ({"data": []}, {}),
    ]
    call_count = 0

    async def fake_get(endpoint, *, params=None, return_headers=True):
        nonlocal call_count
        resp = pages[call_count]
        call_count += 1
        return resp

    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
        lambda *a, **k: MagicMock(initialize=AsyncMock()),
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.TicketTranslator",
        lambda *a, **k: MagicMock(),
    )

    client = GlpiApiClient(session=session)
    monkeypatch.setattr(client._session, "get", AsyncMock(side_effect=fake_get))

    data = await client.get_all_paginated("Ticket", page_size=2)

    assert call_count == 3
    assert data == [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
        {"id": 3, "name": "c"},
    ]


@pytest.mark.asyncio
async def test_get_ticket_summary_by_group(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
        lambda *a, **k: MagicMock(),
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.TicketTranslator",
        lambda *a, **k: MagicMock(),
    )

    fake_data: Dict[str, list[dict]] = {
        "89": [
            {"status": {"name": "New"}},
            {"status": {"name": "New"}},
            {"status": {"name": "Processing (assigned)"}},
        ],
        "90": [
            {"status": {"name": "Solved"}},
            {"status": {"name": "Solved"}},
            {"status": {"name": "New"}},
        ],
        "91": [],
        "92": [
            {"status": {"name": "Pending"}},
        ],
    }

    async def fake_get_all_paginated(itemtype, *, criteria=None, **_):
        group_id = criteria[0]["value"]
        return fake_data[group_id]

    client = GlpiApiClient(session=session)
    monkeypatch.setattr(
        client,
        "get_all_paginated",
        AsyncMock(side_effect=fake_get_all_paginated),
    )

    summary = await client.get_ticket_summary_by_group()

    assert summary["N1"]["new"] == 2
    assert summary["N1"]["processing (assigned)"] == 1
    assert summary["N2"]["solved"] == 2
    assert summary["N2"]["new"] == 1
    assert summary["N3"] == {status: 0 for status in TEXT_STATUS_MAP.keys()}
    assert summary["N4"]["pending"] == 1


@pytest.mark.asyncio
async def test_get_ticket_summary_by_group_network_error(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
        lambda *a, **k: MagicMock(),
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.TicketTranslator",
        lambda *a, **k: MagicMock(),
    )

    client = GlpiApiClient(session=session)
    monkeypatch.setattr(
        client,
        "get_all_paginated",
        AsyncMock(side_effect=Exception("boom")),
    )

    summary = await client.get_ticket_summary_by_group()

    expected = {
        level: {status: 0 for status in TEXT_STATUS_MAP.keys()} for level in GROUP_IDS
    }
    assert summary == expected
