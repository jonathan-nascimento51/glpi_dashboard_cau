import pandas as pd
from fastapi.testclient import TestClient

from app.api import metrics as metrics_module
from worker import create_app


def test_overview_endpoint_alias(monkeypatch):
    tickets = [
        {"id": 1, "status": "new", "group": "N1", "date_creation": "2024-06-01"},
        {
            "id": 2,
            "status": "closed",
            "group": "N1",
            "date_creation": "2024-06-02",
            "date_resolved": "2024-06-03",
        },
    ]

    monkeypatch.setattr(
        metrics_module, "fetch_dataframe", lambda client: pd.DataFrame(tickets)
    )
    app = create_app()
    client = TestClient(app)
    resp = client.get("/metrics/aggregated")
    assert resp.status_code == 200
