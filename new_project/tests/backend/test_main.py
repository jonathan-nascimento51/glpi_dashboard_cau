import importlib.util
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

# Load glpi_session module without executing package __init__ that depends on
# optional py_glpi.
GLPI_PATH = ROOT / "src" / "backend" / "infrastructure" / "glpi" / "glpi_session.py"
spec = importlib.util.spec_from_file_location(
    "backend.infrastructure.glpi.glpi_session", GLPI_PATH
)
assert spec and spec.loader
glpi_session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(glpi_session)
package = types.ModuleType("backend.infrastructure.glpi")
package.glpi_session = glpi_session  # type: ignore[attr-defined]

NORM_PATH = ROOT / "src" / "backend" / "infrastructure" / "glpi" / "normalization.py"
norm_spec = importlib.util.spec_from_file_location(
    "backend.infrastructure.glpi.normalization", NORM_PATH
)
assert norm_spec and norm_spec.loader
normalization = importlib.util.module_from_spec(norm_spec)
norm_spec.loader.exec_module(normalization)
package.normalization = normalization  # type: ignore[attr-defined]

sys.modules["backend.infrastructure.glpi"] = package
sys.modules["backend.infrastructure.glpi.glpi_session"] = glpi_session
sys.modules["backend.infrastructure.glpi.normalization"] = normalization

sys.path.insert(0, str(ROOT / "new_project" / "backend"))
import main as backend_main  # noqa: E402


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
    return TestClient(backend_main.app)


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
