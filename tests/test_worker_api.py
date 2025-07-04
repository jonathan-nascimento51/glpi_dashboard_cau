import os
import sys

import pytest
from fastapi.testclient import TestClient  # noqa: E402
import redis
from glpi_dashboard.services.exceptions import GLPIUnauthorizedError

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

import worker  # noqa: E402
from worker import create_app  # noqa: E402


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


@pytest.fixture(autouse=True)
def patch_cache(monkeypatch: pytest.MonkeyPatch):
    cache = DummyCache()
    monkeypatch.setattr(worker, "redis_client", cache)
    import src.glpi_dashboard.services.worker_api as worker_api

    monkeypatch.setattr(worker_api, "redis_client", cache)
    return cache


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def get_all(self, *args, **kwargs):
        return [{"id": 1}]


def test_rest_endpoints():
    client = TestClient(create_app(client=FakeSession()))
    resp = client.get("/tickets")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "total" in resp.json()


def test_graphql_metrics():
    app = create_app(client=FakeSession())
    paths = [getattr(r, "path", None) for r in app.router.routes if hasattr(r, "path")]
    assert "/graphql/" in paths


def test_graphql_query():
    client = TestClient(create_app(client=FakeSession()))
    query = "{ metrics { total } }"
    resp = client.post("/graphql/", params={"r": ""}, json={"query": query})
    assert resp.status_code == 200
    assert resp.json()["data"]["metrics"]["total"] >= 0


def test_client_reused(monkeypatch: pytest.MonkeyPatch):
    instances = []

    class RecordingSession(FakeSession):
        def __init__(self):
            instances.append(self)

    monkeypatch.setattr(
        "glpi_dashboard.services.worker_api.GlpiApiClient",
        lambda *a, **k: RecordingSession(),
    )

    client = TestClient(create_app(client=RecordingSession()))
    client.get("/tickets")
    client.get("/metrics")

    assert len(instances) == 1


def test_cache_stats_endpoint():
    client = TestClient(create_app(client=FakeSession()))
    client.get("/tickets")
    resp = client.get("/cache/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["misses"] == 2
    assert data["hits"] == 0


def test_cache_middleware():
    client = TestClient(create_app(client=FakeSession()))
    client.get("/tickets")
    client.get("/tickets")
    resp = client.get("/cache/stats")
    data = resp.json()
    assert data["hits"] == 1
    assert data["misses"] == 2


def test_health_glpi(monkeypatch: pytest.MonkeyPatch):
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
    client = TestClient(create_app(client=FakeSession()))
    resp = client.get("/health/glpi")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"


def test_redis_connection_error(monkeypatch: pytest.MonkeyPatch, patch_cache):
    async def raise_conn(*args, **kwargs):
        raise redis.exceptions.ConnectionError("fail")

    monkeypatch.setattr(patch_cache, "get", raise_conn)
    client = TestClient(create_app(client=FakeSession()), raise_server_exceptions=False)
    resp = client.get("/tickets")
    assert resp.status_code == 500
    assert "Internal Server Error" in resp.text


def test_health_glpi_auth_failure(monkeypatch: pytest.MonkeyPatch):
    async def raise_auth(self):
        raise GLPIUnauthorizedError(401, "unauthorized")

    monkeypatch.setattr(
        "glpi_dashboard.services.worker_api.GLPISession.__aenter__",
        raise_auth,
    )
    client = TestClient(create_app(client=FakeSession()), raise_server_exceptions=False)
    resp = client.get("/health/glpi")
    assert resp.status_code == 500
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "GLPI connection failed"
    assert "unauthorized" in data["details"]
