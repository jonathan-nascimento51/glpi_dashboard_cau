import json
import os
import tempfile

import pytest

import scripts.fetch_tickets as fetch_tickets


@pytest.mark.asyncio
async def test_fetch_and_save(monkeypatch, tmp_path):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_all(self, *args, **kwargs):
            return [
                {
                    "id": 1,
                    "status": "new",
                    "group": "N1",
                    "assigned_to": "alice",
                    "date_creation": "2024-01-01",
                }
            ]

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

        async def get_all(self, *args, **kwargs):
            return [{}]

    monkeypatch.setattr(fetch_tickets, "GLPISession", lambda *a, **k: FakeSession())
    out = tmp_path / "bad.json"
    await fetch_tickets.fetch_and_save(output=out)
    with out.open() as f:
        data = json.load(f)
    assert data[0]["id"] == 0
    assert data[0].get("status") == ""


def test_fetch_raw_data_missing_env(monkeypatch, caplog):
    """The script should log an error and abort when credentials are absent."""

    monkeypatch.delenv("GLPI_BASE_URL", raising=False)
    monkeypatch.delenv("GLPI_APP_TOKEN", raising=False)
    monkeypatch.delenv("GLPI_USER_TOKEN", raising=False)

    def fail(*_a, **_kw):  # pragma: no cover - should not be called
        raise AssertionError("network call attempted")

    monkeypatch.setattr(fetch_tickets, "GLPISession", fail)

    caplog.set_level("ERROR")
    fetch_tickets.fetch_raw_data()
    assert "vari\u00e1veis de ambiente" in caplog.text


@pytest.mark.asyncio
async def test_fetch_and_save_tempfile(monkeypatch):
    """Use tempfile.NamedTemporaryFile to validate JSON output."""

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get_all(self, *args, **kwargs):
            return [{"id": 1, "status": "new"}]

    monkeypatch.setattr(fetch_tickets, "GLPISession", lambda *a, **k: FakeSession())

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        out_path = tmp.name

    try:
        await fetch_tickets.fetch_and_save(output=out_path)
        with open(out_path) as f:
            data = json.load(f)
        assert data == [{"id": 1, "status": "new"}]
    finally:
        os.remove(out_path)
