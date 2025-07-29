from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.glpi_api_client import (
    GlpiApiClient,
)


@pytest.mark.asyncio
async def test_populate_forced_fields(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
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
        "backend.application.glpi_api_client.TicketTranslator", MagicMock
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
async def test_get_status_counts_by_levels(monkeypatch):
    session = MagicMock()
    session.get_ticket_counts_by_level = AsyncMock(
        side_effect=lambda lvl: {"new": 1, "pending": 0, "solved": 2}
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
        lambda *a, **k: MagicMock(),
    )
    client = GlpiApiClient(session=session)

    counts = await client.get_status_counts_by_levels(["N1", "N2"])

    assert counts == {
        "N1": {"new": 1, "pending": 0, "solved": 2},
        "N2": {"new": 1, "pending": 0, "solved": 2},
    }
    assert session.get_ticket_counts_by_level.await_count == 2
