import pytest
from fastapi.testclient import TestClient

from tests.test_worker_api import DummyCache
from worker import create_app


@pytest.fixture
def dummy_cache() -> DummyCache:
    return DummyCache()


def test_head_health_ok(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
) -> None:
    async def ok() -> int:
        return 200

    monkeypatch.setattr("src.backend.api.worker_api.check_glpi_connection", ok)
    client = TestClient(create_app(cache=dummy_cache))
    resp = client.head("/health")
    assert resp.status_code == 200
    assert resp.text == ""


def test_health_unavailable(glpi_unavailable, dummy_cache: DummyCache) -> None:
    client = TestClient(create_app(cache=dummy_cache))
    resp = client.get("/health")
    assert resp.status_code == 500
