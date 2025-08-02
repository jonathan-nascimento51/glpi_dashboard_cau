import pytest
from fastapi.testclient import TestClient

import backend.application.aggregated_metrics as aggregated_metrics
from backend.application.glpi_api_client import GlpiApiClient
from backend.schemas.ticket_models import CleanTicketDTO
from src.backend.api import worker_api as worker_module
from src.backend.api.worker_api import create_app, get_glpi_client


class DummyCache:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ttl_seconds=None):
        self.data[key] = value

    def get_cache_metrics(self) -> dict[str, float]:
        return {"hits": 0, "misses": 0, "total": 0, "hit_rate": 0.0}


class FakeClient(GlpiApiClient):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def fetch_tickets(self, *args, **kwargs):
        raw = [
            {
                "id": 1,
                "name": "A",
                "status": 5,
                "priority": 3,
                "date_creation": "2024-06-01T00:00:00",
                "assigned_to": "",
                "group": "N1",
                "requester": "Alice",
                "users_id_requester": 10,
            },
            {
                "id": 2,
                "name": "B",
                "status": 6,
                "priority": 2,
                "date_creation": "2024-06-02T00:00:00",
                "assigned_to": "",
                "group": "N2",
                "requester": "Bob",
                "users_id_requester": 11,
            },
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]


@pytest.fixture
def test_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        aggregated_metrics,
        "map_group_ids_to_labels",
        lambda series: series,
        raising=False,
    )

    async def fake_stream(_client, cache=None, response=None):
        yield b"fetching...\n"
        yield b"done\n"

    monkeypatch.setattr(worker_module, "stream_tickets", fake_stream)
    cache = DummyCache()
    app = create_app(client=FakeClient(), cache=cache)
    app.dependency_overrides[get_glpi_client] = FakeClient
    return TestClient(app)


def test_metrics_summary_endpoint(test_client: TestClient):
    resp = test_client.get("/v1/metrics/summary")
    assert resp.status_code == 200
    assert resp.json() == {"total": 2, "opened": 0, "closed": 2}


def test_tickets_stream_endpoint(test_client: TestClient):
    resp = test_client.get("/v1/tickets/stream")
    assert resp.status_code == 200
    lines = resp.text.splitlines()
    assert lines == ["fetching...", "done"]
