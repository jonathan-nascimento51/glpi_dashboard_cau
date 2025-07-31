import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.application import ticket_loader
from tests.test_worker_api import DummyCache
from worker import create_app


@pytest.fixture
def dummy_cache() -> DummyCache:
    return DummyCache()


def test_head_health_ok(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
) -> None:
    async def fake_load(*args: object, **kwargs: object) -> pd.DataFrame:
        return pd.DataFrame()

    monkeypatch.setattr(ticket_loader, "load_tickets", fake_load)
    with TestClient(create_app(cache=dummy_cache)) as client:
        resp = client.head("/health")
        assert resp.status_code == 200
        assert resp.text == ""


def test_health_unavailable(
    monkeypatch: pytest.MonkeyPatch, dummy_cache: DummyCache
) -> None:
    async def raise_error(*args: object, **kwargs: object) -> pd.DataFrame:
        raise RuntimeError("fail")

    monkeypatch.setattr(ticket_loader, "load_tickets", raise_error)
    with TestClient(create_app(cache=dummy_cache)) as client:
        resp = client.get("/health")
        assert resp.status_code == 503
