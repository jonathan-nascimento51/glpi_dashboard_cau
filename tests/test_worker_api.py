import sys
import types

import pytest
import pytest_asyncio
import redis
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST

from backend.api.worker_api import get_glpi_client
from backend.application import ticket_loader
from backend.application.glpi_api_client import GlpiApiClient
from backend.domain.exceptions import GLPIUnauthorizedError
from shared.dto import CleanTicketDTO
from worker import create_app

pytest.importorskip("prometheus_client")

sys.modules.setdefault(
    "langgraph.checkpoint.sqlite", types.ModuleType("langgraph.checkpoint.sqlite")
)


class DummyCache:
    def __init__(self):
        self.data = {}
        self.hits = 0
        self.misses = 0

    async def get(self, key):
        if key in self.data:
            self.hits += 1
            return self.data[key]
        self.misses += 1
        return None

    async def set(self, key, data, ttl_seconds=None):
        self.data[key] = data

    def get_cache_metrics(self) -> dict[str, float]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": hit_rate,
        }


@pytest.fixture
def dummy_cache() -> DummyCache:
    return DummyCache()


class FakeClient(GlpiApiClient):
    def __init__(self) -> None:
        """Fake client that conforms to the GlpiApiClient interface for tests."""
        pass

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
                "requester": "Bob",
                "users_id_requester": 11,
            },
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]


@pytest_asyncio.fixture
async def test_app(dummy_cache: DummyCache):
    app = create_app(client=FakeClient(), cache=dummy_cache)
    app.dependency_overrides[get_glpi_client] = FakeClient
    yield TestClient(app)


def test_rest_endpoints(test_app: TestClient):
    resp = test_app.get("/tickets")
    assert resp.status_code == 200
    tickets = resp.json()
    assert isinstance(tickets, list)
    assert tickets and "id" in tickets[0]
    assert tickets[0]["requester"] == "Alice"

    resp = test_app.get("/tickets/search", params={"query": "A", "limit": 1})
    assert resp.status_code == 200
    results = resp.json()
    assert results[0]["name"] == "A"
    assert len(results) <= 1

    resp = test_app.get("/metrics/summary")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics == {"total": 2, "opened": 0, "closed": 2}


def test_ticket_search_endpoint(dummy_cache: DummyCache) -> None:
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))

    resp = client.get("/tickets/search", params={"query": "Search"})
    assert resp.status_code == 200
    data = resp.json()
    assert data and data[0]["id"] == 3


def test_aggregated_metrics(dummy_cache: DummyCache):
    dummy_cache.data["metrics_aggregated"] = {"status": {}, "per_user": {}}
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/metrics/aggregated")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "per_user" in data


def test_metrics_router_endpoints(
    monkeypatch: pytest.MonkeyPatch,
    dummy_cache: DummyCache,
) -> None:
    """Ensure metrics overview and level endpoints are accessible via create_app."""
    from app.api.metrics import LevelMetrics, MetricsOverview

    overview = MetricsOverview(
        open_tickets={"N1": 1},
        tickets_closed_this_month={"N1": 1},
        status_distribution={"new": 1},
    )
    level = LevelMetrics(
        open_tickets=1,
        resolved_this_month=1,
        status_distribution={"new": 1},
    )

    async def fake_overview(*args, **kwargs):
        return overview

    async def fake_level_metrics(*args, **kwargs):
        return level

    monkeypatch.setattr("app.api.metrics.compute_overview", fake_overview)
    monkeypatch.setattr("app.api.metrics.compute_level_metrics", fake_level_metrics)

    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/metrics/overview")
    assert resp.status_code == 200
    assert resp.json() == overview.model_dump()

    resp = client.get("/metrics/level/N1")
    assert resp.status_code == 200
    assert resp.json() == level.model_dump()


def test_chamados_por_data(dummy_cache: DummyCache):
    dummy_cache.data["chamados_por_data"] = [
        {"date": "2024-06-01", "total": 1},
        {"date": "2024-06-02", "total": 1},
    ]
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/chamados/por-data")
    assert resp.status_code == 200
    data = resp.json()
    assert data == [
        {"date": "2024-06-01", "total": 1},
        {"date": "2024-06-02", "total": 1},
    ]


def test_chamados_por_dia(dummy_cache: DummyCache):
    dummy_cache.data["chamados_por_dia"] = [
        {"date": "2024-06-01", "total": 1},
        {"date": "2024-06-02", "total": 1},
    ]
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/chamados/por-dia")
    assert resp.status_code == 200
    data = resp.json()
    assert data == [
        {"date": "2024-06-01", "total": 1},
        {"date": "2024-06-02", "total": 1},
    ]


def test_chamados_por_data_cache(dummy_cache: DummyCache):
    session = FakeClient()
    client = TestClient(create_app(client=session, cache=dummy_cache))
    first = client.get("/chamados/por-data").json()

    def later_data(*args, **kwargs):
        raw = [
            {
                "id": 1,
                "name": "X",
                "status": 5,
                "priority": 2,
                "date_creation": "2024-06-03",
                "requester": "Alice",
                "users_id_requester": 10,
            },
            {
                "id": 2,
                "name": "Y",
                "status": 6,
                "priority": 3,
                "date_creation": "2024-06-04",
                "requester": "Bob",
                "users_id_requester": 11,
            },
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]

    session.fetch_tickets = later_data  # type: ignore[assignment]
    second = client.get("/chamados/por-data").json()
    assert first == second
    stats = client.get("/cache/stats").json()
    assert stats["hits"] == 1
    assert stats["misses"] == 2


def test_chamados_por_dia_cache(dummy_cache: DummyCache):
    session = FakeClient()
    client = TestClient(create_app(client=session, cache=dummy_cache))
    first = client.get("/chamados/por-dia").json()

    def later_data(*args, **kwargs):
        raw = [
            {
                "id": 1,
                "name": "X",
                "status": 5,
                "priority": 2,
                "date_creation": "2024-06-03",
                "requester": "Alice",
                "users_id_requester": 10,
            },
            {
                "id": 2,
                "name": "Y",
                "status": 6,
                "priority": 3,
                "date_creation": "2024-06-04",
                "requester": "Bob",
                "users_id_requester": 11,
            },
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]

    session.fetch_tickets = later_data  # type: ignore[assignment]
    second = client.get("/chamados/por-dia").json()
    assert first == second
    stats = client.get("/cache/stats").json()
    assert stats["hits"] == 1
    assert stats["misses"] == 2


@pytest.mark.asyncio
async def test_loader_primes_cache(dummy_cache: DummyCache) -> None:
    """Ensure load_tickets stores plain lists consumable by the API."""
    await ticket_loader.load_tickets(client=FakeClient(), cache=dummy_cache)

    assert isinstance(dummy_cache.data.get("chamados_por_data"), list)
    assert isinstance(dummy_cache.data.get("chamados_por_dia"), list)

    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))

    resp = client.get("/chamados/por-data")
    assert resp.status_code == 200
    assert resp.json() == dummy_cache.data["chamados_por_data"]

    resp = client.get("/chamados/por-dia")
    assert resp.status_code == 200
    assert resp.json() == dummy_cache.data["chamados_por_dia"]


def test_openapi_schema_models(dummy_cache: DummyCache):
    app = create_app(client=FakeClient(), cache=dummy_cache)
    schema = app.openapi()
    por_data = schema["paths"]["/chamados/por-data"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    assert por_data["items"]["$ref"].endswith("ChamadoPorData")
    por_dia = schema["paths"]["/chamados/por-dia"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    assert por_dia["items"]["$ref"].endswith("ChamadosPorDia")


def test_tickets_stream(monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache):
    async def fake_gen(_client):
        yield b"fetching...\n"
        yield b"done\n"

    monkeypatch.setitem(
        create_app.__globals__,
        "_stream_tickets",
        lambda client, cache=None: fake_gen(client),
    )

    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/tickets/stream")
    assert resp.status_code == 200
    assert resp.text.splitlines() == ["fetching...", "done"]


def test_graphql_metrics(dummy_cache: DummyCache):
    app = create_app(client=FakeClient(), cache=dummy_cache)
    paths = [getattr(r, "path", None) for r in app.router.routes if hasattr(r, "path")]
    assert "/graphql/" in paths


def test_graphql_query(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    query = "{ metrics { total } }"
    resp = client.post("/graphql/", params={"r": ""}, json={"query": query})
    assert resp.status_code == 200
    assert resp.json()["data"]["metrics"]["total"] >= 0


def test_client_reused(monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache):
    """
    Verifies that the same GLPI API client instance is reused across multiple
    requests within the application's lifespan.
    """
    instances = []

    class RecordingClient(FakeClient):
        def __init__(self, *args, **kwargs):
            print("RecordingClient.__init__ called")  # Linha de depuração
            super().__init__(*args, **kwargs)
            instances.append(self)

    # We patch the factory function that creates the client
    monkeypatch.setattr(
        "backend.api.worker_api.create_glpi_api_client",
        RecordingClient,
    )

    # Create the app without passing a client, so it uses the patched factory
    client = TestClient(create_app(cache=dummy_cache))
    client.get("/tickets")
    client.get("/metrics/summary")

    # Only one client instance should have been created for the app's lifespan
    assert len(instances) == 1


def test_cache_stats_endpoint(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    client.get("/tickets")
    resp = client.get("/cache/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["misses"] == 2
    assert data["hits"] == 0


def test_cache_middleware(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    client.get("/tickets")
    client.get("/tickets")
    resp = client.get("/cache/stats")
    data = resp.json()
    assert data["hits"] == 1
    assert data["misses"] == 2


def test_health_glpi(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_health_glpi_head_success(dummy_cache: DummyCache) -> None:
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.head("/health")
    assert resp.status_code == 200
    assert resp.text == ""


def test_redis_connection_error(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
):
    async def raise_conn(*args, **kwargs):
        raise redis.exceptions.ConnectionError("fail")

    monkeypatch.setattr(dummy_cache, "get", raise_conn)
    client = TestClient(
        create_app(client=FakeClient(), cache=dummy_cache),
        raise_server_exceptions=False,
    )
    resp = client.get("/tickets")
    assert resp.status_code == 500
    assert "Internal Server Error" in resp.text


def test_health_glpi_auth_failure(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
):
    async def raise_auth(self):
        raise GLPIUnauthorizedError(401, "unauthorized")

    monkeypatch.setattr(
        "backend.application.glpi_api_client.GlpiApiClient.__aenter__",
        raise_auth,
    )
    client = TestClient(
        create_app(client=FakeClient(), cache=dummy_cache),
        raise_server_exceptions=False,
    )
    resp = client.get("/health")
    assert resp.status_code == 500
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "GLPI connection failed"
    assert "unauthorized" in data["details"]


def test_session_init_failure_fallback(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
) -> None:
    async def raise_init(self):
        raise RuntimeError("no network")

    monkeypatch.setattr(
        "backend.application.glpi_api_client.GlpiApiClient.__aenter__",
        raise_init,
    )
    app = create_app(cache=dummy_cache)
    app.dependency_overrides[get_glpi_client] = lambda: None
    client = TestClient(app)

    resp = client.get("/tickets")
    assert resp.status_code == 200
    assert resp.headers.get("X-Warning") == "using mock data"
    tickets = resp.json()
    assert tickets and isinstance(tickets, list)


def test_breaker_content_type(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/breaker")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == CONTENT_TYPE_LATEST


def test_cache_metrics_legacy(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    client.get("/tickets")
    legacy = client.get("/cache-metrics")
    stats = client.get("/cache/stats")
    assert legacy.status_code == 200
    assert legacy.json() == stats.json()


def test_read_model_db_error(monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache):
    """Test that a DB error in the read model returns a 503."""

    async def raise_db_error(*args, **kwargs):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr("backend.api.worker_api.query_ticket_summary", raise_db_error)
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/read-model/tickets")
    assert resp.status_code == 503
    assert "Read model is currently unavailable" in resp.json()["detail"]


def test_metrics_aggregated_cache(dummy_cache: DummyCache):
    dummy_cache.data["metrics_aggregated"] = {"status": {}, "per_user": {}}
    session = FakeClient()
    client = TestClient(create_app(client=session, cache=dummy_cache))
    first = client.get("/metrics/aggregated").json()

    def later_data(*args, **kwargs):
        raw = [
            {
                "id": 99,
                "name": "Z",
                "status": 5,
                "priority": 2,
                "date_creation": "2024-07-01",
                "requester": "Carol",
                "users_id_requester": 12,
            }
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]

    session.fetch_tickets = later_data  # type: ignore[assignment]
    second = client.get("/metrics/aggregated").json()

    assert first == second
    stats = client.get("/cache/stats").json()
    assert stats["hits"] >= 1
