import logging

import pytest

from shared.models import (
    Impact,
    RawTicketDTO,
    TicketStatus,
    TicketType,
    Urgency,
    convert_ticket,
)


@pytest.mark.unit
def test_convert_ticket_enum_mapping() -> None:
    raw = RawTicketDTO(
        id=1,
        name="Ticket",
        content="Test Content",
        status=1,
        priority=2,
        urgency=3,
        impact=4,
        type=1,
        date_creation="2024-01-01",
    )

    ticket = convert_ticket(raw)

    assert ticket.status is TicketStatus.NEW
    assert ticket.priority == "Baixa"
    assert ticket.urgency is Urgency.MEDIUM
    assert ticket.impact is Impact.HIGH
    assert ticket.type is TicketType.INCIDENT


@pytest.mark.unit
def test_convert_ticket_invalid_status_fallback(
    caplog: pytest.LogCaptureFixture,
) -> None:
    raw = RawTicketDTO(
        id=1,
        name="Test Ticket",
        content="Test Content",
        status=99,
        priority=1,
        urgency=1,
        impact=1,
        type=1,
        date_creation="2024-01-01",
    )

    with caplog.at_level(logging.WARNING):
        ticket = convert_ticket(raw)

    assert ticket.status is TicketStatus.UNKNOWN
    assert any(
        "Unknown TicketStatus value: 99" in rec.getMessage() for rec in caplog.records
    )


@pytest.mark.unit
@pytest.mark.parametrize("raw_name", [None, ""])
def test_convert_ticket_missing_name(raw_name: str | None) -> None:
    raw = RawTicketDTO(id=1, name=raw_name)

    ticket = convert_ticket(raw)

    assert ticket.title == "[Título não informado]"
