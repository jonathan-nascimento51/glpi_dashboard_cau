import json

import pytest

import scripts.fetch_tickets as fetch_tickets


@pytest.mark.asyncio
async def test_fetch_and_save(monkeypatch, tmp_path):
    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def get_all(self, *args, **kwargs):
            return [
                {
                    "id": 1,
                    "status": "new",
                    "group": "N1",
                    "assigned_to": "alice",
                    "date_creation": "2024-01-01",
                }
            ]

    monkeypatch.setattr(fetch_tickets, "GlpiApiClient", lambda *a, **k: FakeSession())
    out = tmp_path / "data.json"
    await fetch_tickets.fetch_and_save(output=out)
    with out.open() as f:
        data = json.load(f)
    assert data and data[0]["id"] == 1


@pytest.mark.asyncio
async def test_fetch_and_save_bad_payload(monkeypatch, tmp_path):
    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def get_all(self, *args, **kwargs):
            return [{}]

    monkeypatch.setattr(fetch_tickets, "GlpiApiClient", lambda *a, **k: FakeSession())
    out = tmp_path / "bad.json"
    await fetch_tickets.fetch_and_save(output=out)
    with out.open() as f:
        data = json.load(f)
    assert data[0]["id"] == 0
    assert data[0].get("status") == ""
