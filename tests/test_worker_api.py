import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worker_api import create_app  # noqa: E402


def test_rest_endpoints():
    client = TestClient(create_app())
    resp = client.get('/tickets')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert 'total' in resp.json()


def test_graphql_metrics():
    app = create_app()
    paths = [r.path for r in app.router.routes]
    assert "/graphql" in paths
