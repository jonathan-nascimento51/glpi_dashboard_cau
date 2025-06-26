import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

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
def patch_cache(monkeypatch):
    cache = DummyCache()
    monkeypatch.setattr(worker_api, "redis_client", cache)
    return cache


def test_rest_endpoints():
    client = TestClient(create_app())
    resp = client.get("/tickets")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "total" in resp.json()


def test_graphql_metrics():
    app = create_app()
    paths = [r.path for r in app.router.routes]
    assert "/graphql/" in paths


def test_graphql_query():
    client = TestClient(create_app())
    query = "{ metrics { total } }"
    resp = client.post("/graphql/", params={"r": ""}, json={"query": query})
    assert resp.status_code == 200
    assert resp.json()["data"]["metrics"]["total"] >= 0


def test_missing_file():
    client = TestClient(create_app(data_file=Path("nonexistent.json")))
    resp = client.get("/tickets")
    assert resp.status_code == 404


def test_client_reused(monkeypatch):
    instances = []

    class FakeSession:
        def __init__(self):
            instances.append(self)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return {"data": [{"id": 1}]}

    monkeypatch.setattr(
        "worker_api.GLPISession",
        lambda *a, **k: FakeSession(),
    )

    client = TestClient(create_app(use_api=True))
    client.get("/tickets")
    client.get("/metrics")

    assert len(instances) == 1


def test_cache_stats_endpoint():
    client = TestClient(create_app())
    client.get("/tickets")
    resp = client.get("/cache/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["misses"] == 1
    assert data["hits"] == 0


def test_cache_middleware():
    client = TestClient(create_app())
    client.get("/tickets")
    client.get("/tickets")
    resp = client.get("/cache/stats")
    data = resp.json()
    assert data["hits"] == 1
    assert data["misses"] == 1
