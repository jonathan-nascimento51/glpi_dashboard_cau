from pathlib import Path

import pytest
import requests

from pact import Consumer, Provider


pytest.importorskip("pact")


@pytest.fixture(scope="session")
def ticket_response() -> dict:
    """Example Ticket fixture with all fields."""
    return {
        "id": 123,
        "name": "Example Ticket",
        "content": "Example content",
        "status": 1,
        "urgency": 2,
        "impact": 3,
        "priority": 4,
        "itilcategories_id": 5,
        "type": 1,
        "_users_id_requester": 10,
        "_users_id_assign": 20,
        "_groups_id_requester": 30,
        "date_creation": "2024-01-01 10:00:00",
        "date_mod": "2024-01-01 12:00:00",
    }


@pytest.fixture(scope="session")
def pact_session() -> Consumer:
    """Configure Pact consumer-provider contract."""
    pact_dir = Path("pacts")
    pact_dir.mkdir(exist_ok=True)
    pact = Consumer("Dashboard").has_pact_with(
        Provider("GLPI"),
        pact_dir=str(pact_dir),
    )
    pact.start_service()
    yield pact
    pact.stop_service()


def test_get_ticket_contract(pact_session: Consumer, ticket_response: dict) -> None:
    """Generate Pact for GET /Ticket/123."""
    (
        pact_session.given("Ticket 123 exists")
        .upon_receiving("a request for ticket 123")
        .with_request("GET", "/Ticket/123")
        .will_respond_with(200, body=ticket_response)
    )

    with pact_session:
        response = requests.get(f"{pact_session.uri}/Ticket/123")

    assert response.json() == ticket_response
