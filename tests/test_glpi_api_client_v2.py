from typing import Any, Dict, List, Optional

import pytest

from glpi_api_client import GlpiApiClient
from glpi_ticket_client import GLPITicketClient


class FakeAuth:
    def __init__(self):
        self.called = False

    async def get_session_token(self, force_refresh: bool = False) -> str:
        self.called = True
        return "tok"


class FakeTicketClient(GLPITicketClient):
    def __init__(self):
        self.called_with: Optional[Dict[str, Any]] = None

    def list_tickets(
        self,
        filters: Optional[Dict[str, str]] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict[str, Any]]:
        self.called_with = {
            "filters": filters,
            "page": page,
            "page_size": page_size,
        }
        return [{"id": 1, "status": 2}]


class FakeEnrichment:
    def __init__(self):
        self.called = False

    async def enrich_tickets(
        self, tickets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        self.called = True
        for t in tickets:
            t["status_name"] = "Ok"
        return tickets

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_get_tickets_flow():
    auth = FakeAuth()
    ticket_client = FakeTicketClient()
    enrichment = FakeEnrichment()
    client = GlpiApiClient(
        auth_client=auth, ticket_client=ticket_client, enrichment=enrichment
    )  # type: ignore[arg-type]

    async with client:
        tickets = await client.get_tickets({"status": "new"}, page=2, page_size=10)

    assert ticket_client.called_with == {
        "filters": {"status": "new"},
        "page": 2,
        "page_size": 10,
    }
    assert enrichment.called
    assert tickets[0]["status_name"] == "Ok"
    assert auth.called
