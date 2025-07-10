import sys
import types

import pytest
import redis
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST

from backend.api.worker_api import get_glpi_client
from backend.services import ticket_loader
from backend.services.exceptions import GLPIUnauthorizedError
from shared.dto import CleanTicketDTO
from worker import create_app

sys.modules.setdefault(
    "langgraph.checkpoint.sqlite", types.ModuleType("langgraph.checkpoint.sqlite")
)
sys.modules["langgraph.checkpoint.sqlite"].SqliteSaver = object  # type: ignore[attr-defined]


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

    def get_cache_metrics(self):
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


class FakeClient:
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
            },
            {
                "id": 2,
                "name": "B",
                "status": 6,
                "priority": 2,
                "date_creation": "2024-06-02T00:00:00",
                "assigned_to": "",
            },
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]


def test_rest_endpoints(dummy_cache: DummyCache):
    app = create_app(client=FakeClient(), cache=dummy_cache)
    app.dependency_overrides[get_glpi_client] = lambda: FakeClient()
    client = TestClient(app)

    resp = client.get("/tickets")
    assert resp.status_code == 200
    tickets = resp.json()
    assert isinstance(tickets, list)
    assert tickets and "id" in tickets[0]

    resp = client.get("/metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics == {"total": 2, "opened": 0, "closed": 2}


def test_aggregated_metrics(dummy_cache: DummyCache):
    dummy_cache.data["metrics_aggregated"] = {"status": {}, "per_user": {}}
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/metrics/aggregated")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "per_user" in data


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
            },
            {
                "id": 2,
                "name": "Y",
                "status": 6,
                "priority": 3,
                "date_creation": "2024-06-04",
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
            },
            {
                "id": 2,
                "name": "Y",
                "status": 6,
                "priority": 3,
                "date_creation": "2024-06-04",
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
    instances = []

    class RecordingSession(FakeClient):
        def __init__(self):
            instances.append(self)

    monkeypatch.setattr(
        "backend.api.worker_api.GlpiApiClient",
        lambda *a, **k: RecordingSession(),
    )

    client = TestClient(create_app(client=RecordingSession(), cache=dummy_cache))
    client.get("/tickets")
    client.get("/metrics")

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


def test_health_glpi(monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache):
    async def fake_enter(self):
        return self

    async def fake_exit(self, exc_type, exc, tb):
        return False

    monkeypatch.setattr(
        "backend.services.glpi_api_client.GlpiApiClient.__aenter__",
        fake_enter,
    )
    monkeypatch.setattr(
        "backend.services.glpi_api_client.GlpiApiClient.__aexit__",
        fake_exit,
    )
    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.get("/health/glpi")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_health_glpi_head_success(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
) -> None:
    async def fake_enter(self):
        return self

    async def fake_exit(self, exc_type, exc, tb):
        return False

    monkeypatch.setattr(
        "backend.services.glpi_api_client.GlpiApiClient.__aenter__",
        fake_enter,
    )
    monkeypatch.setattr(
        "backend.services.glpi_api_client.GlpiApiClient.__aexit__",
        fake_exit,
    )

    client = TestClient(create_app(client=FakeClient(), cache=dummy_cache))
    resp = client.head("/health/glpi")
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
        "backend.services.glpi_api_client.GlpiApiClient.__aenter__",
        raise_auth,
    )
    client = TestClient(
        create_app(client=FakeClient(), cache=dummy_cache),
        raise_server_exceptions=False,
    )
    resp = client.get("/health/glpi")
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
        "backend.services.glpi_api_client.GlpiApiClient.__aenter__",
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
            }
        ]
        return [CleanTicketDTO.model_validate(r) for r in raw]

    session.fetch_tickets = later_data  # type: ignore[assignment]
    second = client.get("/metrics/aggregated").json()

    assert first == second
    stats = client.get("/cache/stats").json()
    assert stats["hits"] >= 1
