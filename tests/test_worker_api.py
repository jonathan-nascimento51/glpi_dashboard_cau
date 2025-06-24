import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
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
