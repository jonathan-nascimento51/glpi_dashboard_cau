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
    async def noop(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr("backend.application.ticket_loader.load_tickets", noop)
    with TestClient(create_app(cache=dummy_cache)) as client:
        client.app.state.ready = True
        resp = client.head("/health")
        assert resp.status_code == 200
        assert resp.text == ""


def test_health_unavailable(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
) -> None:
    async def noop(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr("backend.application.ticket_loader.load_tickets", noop)
    with TestClient(create_app(cache=dummy_cache)) as client:
        client.app.state.ready = False
        resp = client.get("/health")
        assert resp.status_code == 503
