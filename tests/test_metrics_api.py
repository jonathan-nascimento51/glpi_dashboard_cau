import importlib
import sys
import types

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeTicket:
    def __init__(self, **data):
        self.__dict__.update(data)

    def model_dump(self):
        return self.__dict__


class DummyCache:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ttl_seconds=None):
        self.data[key] = value


class FakeClient:
    def __init__(self, items):
        self._items = items
        self.calls = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def fetch_tickets(self):
        self.calls += 1
        return [FakeTicket(**i) for i in self._items]


sample_tickets = [
    {"id": 1, "status": "new", "group": "N1", "date_creation": "2024-06-10"},
    {"id": 2, "status": "closed", "group": "N1", "date_creation": "2024-06-05"},
    {"id": 3, "status": "pending", "group": "N2", "date_creation": "2024-05-20"},
    {"id": 4, "status": "closed", "group": "N2", "date_creation": "2024-06-02"},
]


@pytest.fixture
def test_client(monkeypatch):
    cache = DummyCache()
    client = FakeClient(sample_tickets)

    # Create dummy module before importing metrics
    fake_module = types.SimpleNamespace(
        create_glpi_api_client=lambda: client, GlpiApiClient=object
    )
    sys.modules["backend.application.glpi_api_client"] = fake_module  # type: ignore[assignment]

    def fake_process(data):
        df = pd.DataFrame(data)
        if "date_creation" in df.columns:
            df["date_creation"] = pd.to_datetime(df["date_creation"])
        return df

    fake_norm = types.SimpleNamespace(process_raw=fake_process)
    sys.modules["backend.infrastructure.glpi.normalization"] = fake_norm  # type: ignore[assignment]
    fake_redis = types.SimpleNamespace(RedisClient=object, redis_client=cache)
    sys.modules["shared.utils.redis_client"] = fake_redis  # type: ignore[assignment]

    metrics_module = importlib.import_module("app.api.metrics")
    monkeypatch.setattr(metrics_module, "redis_client", cache)

    api_pkg = importlib.import_module("app.api")
    app = FastAPI()
    app.include_router(api_pkg.router)
    return TestClient(app), client, cache, metrics_module


def test_overview_endpoint(test_client):
    client, api_client, cache, metrics_module = test_client
    resp = client.get("/metrics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["open_tickets"] == {"N1": 1, "N2": 1}
    assert data["resolved_this_month"] == {}
    assert data["status_distribution"] == {"new": 1, "closed": 2, "pending": 1}
    # call again should hit cache
    resp = client.get("/metrics/overview")
    assert resp.status_code == 200
    assert api_client.calls == 1


def test_level_endpoint(test_client):
    client, api_client, cache, metrics_module = test_client
    resp = client.get("/metrics/level/N1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["open_tickets"] == 1
    assert data["resolved_this_month"] == 0


def test_error_handling(monkeypatch, test_client):
    client, api_client, cache, metrics_module = test_client

    async def fail(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(metrics_module, "_fetch_dataframe", fail)
    resp = client.get("/metrics/overview")
    assert resp.status_code == 500
