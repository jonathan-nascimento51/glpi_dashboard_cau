from unittest.mock import AsyncMock

import pytest

from shared.dto import CleanTicketDTO
from src.backend.services import ticket_loader


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

    translator = mocker.Mock()
    translator.mapper = mocker.Mock()
    translator.translate_ticket = AsyncMock()

    result = await ticket_loader.load_and_translate_tickets(translator, cache=cache)

    assert isinstance(result, list)
    assert all(isinstance(t, CleanTicketDTO) for t in result)
    translator.translate_ticket.assert_not_awaited()
    cache.get.assert_awaited_once_with("tickets_clean")
