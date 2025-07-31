import importlib
import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
PKG_SPEC = importlib.util.spec_from_file_location(
    "new_project", ROOT / "new_project" / "__init__.py"
)
assert PKG_SPEC and PKG_SPEC.loader
new_project_pkg = importlib.util.module_from_spec(PKG_SPEC)
PKG_SPEC.loader.exec_module(new_project_pkg)
new_project_pkg.__path__ = [str(ROOT / "new_project")]
sys.modules["new_project"] = new_project_pkg

backend_main = importlib.import_module("new_project.backend.main")
from new_project.backend.metrics import LevelMetrics, MetricsOverview  # noqa: E402


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get_all_paginated(self, itemtype: str, page_size: int = 100, **params):
        return [
            {
                "id": 1,
                "name": "A",
                "status": "new",
                "group": "N1",
                "assigned_to": "",
                "requester": "Alice",
                "date_creation": "2024-06-01",
            },
            {
                "id": 2,
                "name": "B",
                "status": "closed",
                "group": "N1",
                "assigned_to": "",
                "requester": "Bob",
                "date_creation": "2024-06-02",
            },
        ]


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(backend_main, "create_session", lambda: DummySession())

    def fake_overview(*args: object, **kwargs: object) -> MetricsOverview:
        return MetricsOverview(
            open_tickets={"N1": 1},
            tickets_closed_this_month={"N1": 1},
            status_distribution={"new": 1, "closed": 1},
        )

    def fake_level_metrics(*args: object, **kwargs: object) -> LevelMetrics:
        return LevelMetrics(
            open_tickets=1,
            resolved_this_month=1,
            status_distribution={"new": 1, "closed": 1},
        )

    monkeypatch.setattr(backend_main, "compute_overview", fake_overview)
    monkeypatch.setattr(backend_main, "compute_level_metrics", fake_level_metrics)

    return TestClient(backend_main.app)


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_tickets_endpoint(client: TestClient) -> None:
    resp = client.get("/tickets")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["id"] == 1
    assert data[1]["status"] == "closed"


def test_metrics_endpoint(client: TestClient) -> None:
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert resp.json() == {"total": 2, "opened": 1, "closed": 1}


def test_metrics_overview_endpoint(client: TestClient) -> None:
    resp = client.get("/metrics/overview")
    assert resp.status_code == 200
    assert resp.json() == {
        "open_tickets": {"N1": 1},
        "tickets_closed_this_month": {"N1": 1},
        "status_distribution": {"new": 1, "closed": 1},
    }


def test_metrics_level_endpoint(client: TestClient) -> None:
    resp = client.get("/metrics/level/N1")
    assert resp.status_code == 200
    assert resp.json() == {
        "open_tickets": 1,
        "resolved_this_month": 1,
        "status_distribution": {"new": 1, "closed": 1},
    }
