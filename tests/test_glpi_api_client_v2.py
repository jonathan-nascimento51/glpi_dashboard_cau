import pytest

# mypy: disable-error-code=arg-type
from glpi_api_client import GlpiApiClient


class FakeAuth:
    def __init__(self):
        self.called = False

    async def get_session_token(self, force_refresh: bool = False):
        self.called = True
        return "tok"


class FakeTicketClient:
    def __init__(self):
        self.called_with = None

    def list_tickets(self, filters=None, page=1, page_size=50):
        self.called_with = {
            "filters": filters,
            "page": page,
            "page_size": page_size,
        }
        return [{"id": 1, "status": 2}]


class FakeEnrichment:
    def __init__(self):
        self.called = False

    async def enrich_tickets(self, tickets):
        self.called = True
        for t in tickets:
            t["status_name"] = "Ok"
        return tickets

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_get_tickets_flow():
    auth = FakeAuth()
    ticket_client = FakeTicketClient()
    enrichment = FakeEnrichment()
    client = GlpiApiClient(  # type: ignore[misc]
        auth_client=auth, ticket_client=ticket_client, enrichment=enrichment
    )

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
