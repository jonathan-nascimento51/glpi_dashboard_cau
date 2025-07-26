from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.application.glpi_api_client import (
    BASE_TICKET_FIELDS,
    GlpiApiClient,
)


@pytest.mark.asyncio
async def test_populate_forced_fields(monkeypatch):
    session = MagicMock()
    mapper = MagicMock()
    mapper.initialize = AsyncMock()
    mapper.get_ticket_field_ids = AsyncMock(return_value=[1, 2, 3, 4, 5, 6])
    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService", lambda *a, **k: mapper
    )

    client = GlpiApiClient(session=session)
    await client._populate_forced_fields()

    assert client._forced_fields == [1, 2, 3, 4, 5, 6]
    mapper.get_ticket_field_ids.assert_awaited_once_with(BASE_TICKET_FIELDS)


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
