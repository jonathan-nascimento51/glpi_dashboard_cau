import pytest
import redis
from fastapi.testclient import TestClient

from glpi_dashboard.services.exceptions import GLPIUnauthorizedError
from worker import create_app


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


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def get_all(self, *args, **kwargs):
        return [{"id": 1}]


def test_rest_endpoints(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeSession(), cache=dummy_cache))

    resp = client.get("/tickets")
    assert resp.status_code == 200
    tickets = resp.json()
    assert isinstance(tickets, list)
    assert tickets and "id" in tickets[0]

    resp = client.get("/metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics["total"] >= 0


def test_tickets_stream(monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache):
    async def fake_gen(_client):
        yield b"fetching...\n"
        yield b"done\n"

    monkeypatch.setitem(
        create_app.__globals__,
        "_stream_tickets",
        lambda client, cache=None: fake_gen(client),
    )

    client = TestClient(create_app(client=FakeSession(), cache=dummy_cache))
    resp = client.get("/tickets/stream")
    assert resp.status_code == 200
    assert resp.text.splitlines() == ["fetching...", "done"]


def test_graphql_metrics(dummy_cache: DummyCache):
    app = create_app(client=FakeSession(), cache=dummy_cache)
    paths = [getattr(r, "path", None) for r in app.router.routes if hasattr(r, "path")]
    assert "/graphql/" in paths


def test_graphql_query(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeSession(), cache=dummy_cache))
    query = "{ metrics { total } }"
    resp = client.post("/graphql/", params={"r": ""}, json={"query": query})
    assert resp.status_code == 200
    assert resp.json()["data"]["metrics"]["total"] >= 0


def test_client_reused(monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache):
    instances = []

    class RecordingSession(FakeSession):
        def __init__(self):
            instances.append(self)

    monkeypatch.setattr(
        "glpi_dashboard.services.worker_api.GlpiApiClient",
        lambda *a, **k: RecordingSession(),
    )

    client = TestClient(create_app(client=RecordingSession(), cache=dummy_cache))
    client.get("/tickets")
    client.get("/metrics")

    assert len(instances) == 1


def test_cache_stats_endpoint(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeSession(), cache=dummy_cache))
    client.get("/tickets")
    resp = client.get("/cache/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["misses"] == 2
    assert data["hits"] == 0


def test_cache_middleware(dummy_cache: DummyCache):
    client = TestClient(create_app(client=FakeSession(), cache=dummy_cache))
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
        "glpi_dashboard.services.worker_api.GLPISession.__aenter__",
        fake_enter,
    )
    monkeypatch.setattr(
        "glpi_dashboard.services.worker_api.GLPISession.__aexit__",
        fake_exit,
    )
    client = TestClient(create_app(client=FakeSession(), cache=dummy_cache))
    resp = client.get("/health/glpi")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_redis_connection_error(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
):
    async def raise_conn(*args, **kwargs):
        raise redis.exceptions.ConnectionError("fail")

    monkeypatch.setattr(dummy_cache, "get", raise_conn)
    client = TestClient(
        create_app(client=FakeSession(), cache=dummy_cache),
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
        "glpi_dashboard.services.worker_api.GLPISession.__aenter__",
        raise_auth,
    )
    client = TestClient(
        create_app(client=FakeSession(), cache=dummy_cache),
        raise_server_exceptions=False,
    )
    resp = client.get("/health/glpi")
    assert resp.status_code == 500
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "GLPI connection failed"
    assert "unauthorized" in data["details"]
