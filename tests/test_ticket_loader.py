from unittest.mock import AsyncMock

import pytest

from backend.application import ticket_loader
from shared.dto import CleanTicketDTO


@pytest.mark.asyncio
async def test_load_and_translate_tickets_cache_hit(mocker):
    cached = {
        "data": [
            {
                "id": 1,
                "name": "Printer issue",
                "status": 1,
                "priority": 2,
                "date_creation": "2024-01-01T00:00:00",
                "assigned_to": "Alice",
            }
        ]
    }
    cache = mocker.Mock()
    cache.get = AsyncMock(return_value=cached)
    cache.set = AsyncMock()

    result = await ticket_loader.load_and_translate_tickets(cache=cache)

    assert isinstance(result, list)
    assert all(isinstance(t, CleanTicketDTO) for t in result)
    cache.get.assert_awaited_once_with("tickets_clean")


@pytest.mark.asyncio
async def test_check_glpi_connection_mock(monkeypatch):
    """Return 200 without session when mock data is enabled."""

    called = False

    def fake_create_session():
        nonlocal called
        called = True
        raise RuntimeError("should not be called")

    monkeypatch.setattr(ticket_loader, "USE_MOCK_DATA", True)
    monkeypatch.setattr(ticket_loader, "create_glpi_session", fake_create_session)

    status = await ticket_loader.check_glpi_connection()
    assert status == 200
    assert not called
