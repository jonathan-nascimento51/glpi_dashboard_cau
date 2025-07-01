import json
import os
import sys
import pytest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

import scripts.fetch_tickets as fetch_tickets  # noqa: E402


@pytest.mark.asyncio
async def test_fetch_and_save(monkeypatch, tmp_path):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return {
                "data": [
                    {
                        "id": 1,
                        "status": "new",
                        "group": "N1",
                        "assigned_to": "alice",
                        "date_creation": "2024-01-01",
                    }
                ]
            }

    monkeypatch.setattr(fetch_tickets, "GLPISession", lambda *a, **k: FakeSession())
    out = tmp_path / "data.json"
    await fetch_tickets.fetch_and_save(output=out)
    with out.open() as f:
        data = json.load(f)
    assert data and data[0]["id"] == 1


@pytest.mark.asyncio
async def test_fetch_and_save_bad_payload(monkeypatch, tmp_path):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return {"data": [{}]}

    monkeypatch.setattr(fetch_tickets, "GLPISession", lambda *a, **k: FakeSession())
    out = tmp_path / "bad.json"
    await fetch_tickets.fetch_and_save(output=out)
    with out.open() as f:
        data = json.load(f)
    assert data[0]["id"] is None
    assert data[0].get("status") is None
