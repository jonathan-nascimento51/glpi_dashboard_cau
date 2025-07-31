import pytest
from fastapi.testclient import TestClient

from tests.test_worker_api import DummyCache
from worker import create_app


@pytest.fixture
def dummy_cache() -> DummyCache:
    return DummyCache()


def test_head_health_ok(dummy_cache: DummyCache) -> None:
    app = create_app(cache=dummy_cache)
    app.state.ready = True
    client = TestClient(app)
    resp = client.head("/health")
    assert resp.status_code == 200
    assert resp.text == ""


def test_health_unavailable(dummy_cache: DummyCache) -> None:
    app = create_app(cache=dummy_cache)
    app.state.ready = False
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 503
