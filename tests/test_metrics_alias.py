import pytest
from fastapi.testclient import TestClient

worker = pytest.importorskip("worker")
create_app = worker.create_app
worker_api = pytest.importorskip("src.backend.api.worker_api")


async def fake_get_cached_aggregated(cache, key):
    return {"status": {"new": 1}}


def test_overview_endpoint_alias(monkeypatch):
    monkeypatch.setattr(worker_api, "get_cached_aggregated", fake_get_cached_aggregated)
    app = create_app()
    client = TestClient(app)
    resp = client.get("/v1/metrics/aggregated")
    assert resp.status_code == 200
