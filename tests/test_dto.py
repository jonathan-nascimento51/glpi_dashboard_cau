from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from backend.adapters.mapping_service import MappingService
from shared.dto import CleanTicketDTO, TicketTranslator


@pytest.fixture
def mock_mapping_service() -> AsyncMock:
    """Fixture for a mocked MappingService."""
    service = AsyncMock(spec=MappingService)
    service.get_username.return_value = "Test User"
    return service


@pytest.mark.asyncio
async def test_translate_ticket_success(mock_mapping_service: AsyncMock) -> None:
    """Tests successful translation of a raw ticket."""
    translator = TicketTranslator(mock_mapping_service)
    raw_ticket: dict[str, int | str] = {
        "id": 1,
        "name": "Test Ticket",
        "status": 1,  # New
        "priority": 3,  # Medium
        "date_creation": "2024-01-01T12:00:00Z",
        "users_id_assign": 42,
        "users_id_requester": 7,
    }
    translated_ticket = await translator.translate_ticket(raw_ticket)
    assert isinstance(translated_ticket, CleanTicketDTO)
    assert translated_ticket.id == 1
    assert translated_ticket.title == "Test Ticket"
    assert translated_ticket.status == "New"
    assert translated_ticket.priority == "Medium"
    assert translated_ticket.created_at == datetime.fromisoformat(
        "2024-01-01T12:00:00+00:00"
    )
    assert translated_ticket.assigned_to == "Test User"
    assert translated_ticket.requester == "Test User"
    mock_mapping_service.get_username.assert_awaited()
    assert mock_mapping_service.get_username.await_count == 2
