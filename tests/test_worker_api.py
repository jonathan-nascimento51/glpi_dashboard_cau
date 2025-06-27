import os
import sys

import pytest
from fastapi.testclient import TestClient  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from src.glpi_dashboard.services.glpi_session import Credentials, GLPISession
import worker_api  # noqa: E402
from worker_api import create_app  # noqa: E402


class DummyCache:
    def __init__(self):
        self.data = {}
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.data:
            self.hits += 1
            return self.data[key]
        self.misses += 1
        return None

    def set(self, key, data, ttl_seconds=None):
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
    monkeypatch.setattr(worker_api, "redis_client", cache)
    monkeypatch.setattr("src.glpi_dashboard.services.worker_api.redis_client", cache)
    return cache


class FakeSession(GLPISession):
    def __init__(self):
        super().__init__(
            base_url="http://example.com/apirest.php",
            credentials=Credentials(app_token="dummy_app_token", username="test", password="test"),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, *args, **kwargs):
        return {"data": [{"id": 1}]}


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
        "src.glpi_dashboard.services.worker_api.GLPISession",
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
