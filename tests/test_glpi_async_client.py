from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession


class DummyCM:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyResponse:
    def __init__(self, status: int, data: dict | None = None):
        self.status = status
        self._data = data or {}
        self.headers: dict[str, str] = {}
        # Adiciona atributos necessários para ClientResponseError
        self.request_info = MagicMock()
        self.history = ()

    async def json(self):
        return self._data

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                self.request_info,
                self.history,
                status=self.status,
                message="Simulated HTTP Error",
            )


@pytest.mark.asyncio
async def test_request_retry_on_503(monkeypatch):
    responses = [
        DummyResponse(503),
        DummyResponse(503),
        DummyResponse(200, {"ok": True}),
    ]

    async def fake_request(*_a, **_kw):
        return DummyCM(responses.pop(0))

    monkeypatch.setattr(
        "backend.infrastructure.glpi.glpi_session.aiohttp.ClientSession.request",
        lambda *a, **k: fake_request(),
    )

    creds = Credentials(app_token="app", user_token="tok")
    client = GLPISession("http://example.com/api", creds)
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        resp = await client._request("GET", "ping")

    assert resp == {"ok": True}
    assert sleep_mock.call_count == 2


@pytest.mark.asyncio
async def test_request_retry_on_timeout(monkeypatch):
    calls = [0]

    async def fake_request(*_a, **_kw):
        if calls[0] == 0:
            calls[0] += 1
            raise aiohttp.ClientError("boom")
        return DummyCM(DummyResponse(200, {"ok": True}))

    monkeypatch.setattr(
        "backend.infrastructure.glpi.glpi_session.ClientSession.request",
        lambda *a, **k: fake_request(),
    )

    creds = Credentials(app_token="app", user_token="tok")
    client = GLPISession("http://example.com/api", creds)
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        resp = await client._request("GET", "ping")

    assert resp == {"ok": True}
    assert sleep_mock.call_count == 1
