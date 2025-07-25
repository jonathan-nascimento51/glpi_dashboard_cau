import pytest
from pydantic import ValidationError

from shared.dto import CleanTicketDTO


@pytest.mark.unit
def test_clean_ticket_dto_valid_creation():
    data = {
        "id": 1,
        "name": "Printer issue",
        "status": 1,
        "priority": 2,
        "date_creation": "2024-01-01T12:00:00",
        "assigned_to": "Alice",
        "requester": "Alice",
    }

    ticket = CleanTicketDTO.model_validate(data)

    assert ticket.id == 1
    assert ticket.title == "Printer issue"
    assert ticket.status == "New"
    assert ticket.priority == "Low"
    assert ticket.assigned_to == "Alice"
    assert ticket.requester == "Alice"


@pytest.mark.unit
def test_clean_ticket_dto_invalid_types():
    data = {
        "id": "not int",
        "name": "Bad",
        "status": "not int",
        "priority": 1,
        "date_creation": "2024-01-01T12:00:00",
    }

    with pytest.raises(ValidationError):
        CleanTicketDTO.model_validate(data)


@pytest.mark.unit
def test_clean_ticket_dto_missing_required_field():
    data = {
        "id": 1,
        "status": 1,
        "priority": 2,
        "date_creation": "2024-01-01T12:00:00",
    }

    ticket = CleanTicketDTO.model_validate(data)

    assert ticket.title == "[Título não informado]"


@pytest.mark.unit
def test_clean_ticket_dto_none_name_becomes_empty_string():
    """Ensure None titles are sanitized to an empty string."""

    data = {
        "id": 1,
        "name": None,
        "status": 1,
    }

    ticket = CleanTicketDTO.model_validate(data)

    assert ticket.title == ""


@pytest.mark.unit
def test_clean_ticket_dto_missing_optional_fields():
    data = {
        "id": 2,
        "name": "Network issue",
        "status": 1,
    }

    ticket = CleanTicketDTO.model_validate(data)

    assert ticket.priority is None
    assert ticket.created_at is None
    assert ticket.requester is None


@pytest.mark.unit
def test_clean_ticket_dto_text_status():
    """Textual status values should be normalized."""

    data = {
        "id": 3,
        "name": "Network issue",
        "status": "closed",
    }

    ticket = CleanTicketDTO.model_validate(data)

    assert ticket.status == "Closed"


@pytest.mark.unit
def test_clean_ticket_dto_preconverted_priority():
    data = {
        "id": 4,
        "name": "Router",
        "status": 1,
        "priority": "Alta",
    }

    ticket = CleanTicketDTO.model_validate(data)

    assert ticket.priority == "Alta"
