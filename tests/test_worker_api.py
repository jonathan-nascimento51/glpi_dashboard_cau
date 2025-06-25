import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient  # noqa: E402
from pathlib import Path  # noqa: E402
from worker_api import create_app  # noqa: E402


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

    class FakeClient:
        def __init__(self):
            instances.append(self)

        def start_session(self):
            pass

        def search(self, entity, criteria=None, range_="0-99"):
            return [
                {
                    "id": 1,
                    "status": "new",
                    "group": "N1",
                    "date_creation": "2024-01-01",
                    "assigned_to": "alice",
                    "name": "t1",
                }
            ]

    monkeypatch.setattr("worker_api.GLPIClient", FakeClient)

    client = TestClient(create_app(use_api=True))
    client.get("/tickets")
    client.get("/metrics")

    assert len(instances) == 1
