import pytest

from backend.adapters.mapping_service import MappingService
from shared.dto import CleanTicketDTO, TicketTranslator


@pytest.mark.asyncio
async def test_translate_ticket_maps_values(mocker):
    mapper = mocker.Mock(spec=MappingService)
    mapper.get_username = mocker.AsyncMock(return_value="Alice")
    mapper.priority_label = mocker.Mock(return_value="High")

    translator = TicketTranslator(mapper)
    raw = {
        "id": 1,
        "name": "Printer issue",
        "status": 2,
        "priority": 4,
        "date_creation": "2024-01-01T00:00:00",
        "users_id_assign": 5,
    }

    ticket = await translator.translate_ticket(raw)

    assert isinstance(ticket, CleanTicketDTO)
    assert ticket.title == "Printer issue"
    assert ticket.status == "Processing (assigned)"
    assert ticket.priority == "High"
    assert ticket.assigned_to == "Alice"


@pytest.mark.asyncio
async def test_translate_ticket_unassigned(mocker):
    mapper = mocker.Mock(spec=MappingService)
    mapper.get_username = mocker.AsyncMock(return_value="Bob")

    translator = TicketTranslator(mapper)
    raw = {
        "id": 2,
        "name": "Laptop request",
        "status": 1,
        "priority": 3,
        "date_creation": "2024-01-02T00:00:00",
        "users_id_assign": None,
    }

    ticket = await translator.translate_ticket(raw)

    assert ticket.assigned_to == "Unassigned"


@pytest.mark.asyncio
async def test_translate_ticket_uses_priority_label(mocker):
    mapper = mocker.Mock(spec=MappingService)
    mapper.get_username = mocker.AsyncMock(return_value="Bob")
    mapper.priority_label = mocker.Mock(return_value="Alta")

    translator = TicketTranslator(mapper)
    raw = {
        "id": 3,
        "name": "Network issue",
        "status": 1,
        "priority": 4,
        "date_creation": "2024-01-03T00:00:00",
        "users_id_assign": None,
    }

    ticket = await translator.translate_ticket(raw)

    mapper.priority_label.assert_called_once_with(4)
    assert ticket.priority == "Alta"
