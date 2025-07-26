from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.glpi_api_client import (
    BASE_TICKET_FIELDS,
    GlpiApiClient,
)


@pytest.mark.asyncio
async def test_populate_forced_fields_cache_hit(monkeypatch):
    session = MagicMock()
    search_cache = MagicMock()
    search_cache.get = AsyncMock(return_value=[7, 8, 9])
    search_cache.set = AsyncMock()
    mapper = MagicMock(search_cache=search_cache, cache_ttl_seconds=86400)
    mapper.get_ticket_field_ids = AsyncMock()
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService", lambda *a, **k: mapper
    )

    client = GlpiApiClient(session=session)
    await client._populate_forced_fields()

    assert client._forced_fields == [7, 8, 9]
    mapper.get_ticket_field_ids.assert_not_called()
    search_cache.set.assert_not_called()


@pytest.mark.asyncio
async def test_populate_forced_fields_lookup(monkeypatch):
    session = MagicMock()
    search_cache = MagicMock()
    search_cache.get = AsyncMock(return_value=None)
    search_cache.set = AsyncMock()
    mapper = MagicMock(search_cache=search_cache, cache_ttl_seconds=86400)
    mapper.get_ticket_field_ids = AsyncMock(return_value=[1, 2, 3, 4, 5, 6])
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService", lambda *a, **k: mapper
    )

    client = GlpiApiClient(session=session)
    await client._populate_forced_fields()

    assert client._forced_fields == [1, 2, 3, 4, 5, 6]
    mapper.get_ticket_field_ids.assert_awaited_once_with(BASE_TICKET_FIELDS)
    search_cache.set.assert_awaited_once()


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
    mapper = MagicMock()
    mapper.get_search_options = AsyncMock(
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
        lambda *a, **k: mapper,
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
