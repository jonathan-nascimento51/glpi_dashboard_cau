import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

import scripts.fetch_tickets as fetch_tickets  # noqa: E402


def test_fetch_and_save(monkeypatch, tmp_path):
    class FakeClient:
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

    monkeypatch.setattr(fetch_tickets, "GLPIClient", FakeClient)
    out = tmp_path / "data.json"
    fetch_tickets.fetch_and_save(output=out)
    with out.open() as f:
        data = json.load(f)
    assert data and data[0]["id"] == 1
