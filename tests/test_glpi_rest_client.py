from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from backend.adapters.glpi_session import Credentials, GLPISession


class DummyCM:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyResponse:
    def __init__(self, status: int, data=None):
        self.status = status
        self._data = data or {}
        self.headers: dict[str, str] = {}

    async def json(self):
        return self._data

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(None, (), status=self.status)


@pytest.mark.asyncio
async def test_list_search_options(monkeypatch):
    session = GLPISession(
        "http://example.com/apirest.php", Credentials(app_token="app", user_token="tok")
    )

    async def fake_request(method, url, **kwargs):
        assert method == "GET"
        assert url.endswith("listSearchOptions/Ticket")
        return DummyCM(DummyResponse(200, {"1": {"name": "ID", "datatype": "int"}}))

    monkeypatch.setattr(
        "backend.adapters.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    data = await session.list_search_options("Ticket")
    assert data["1"]["name"] == "ID"


@pytest.mark.asyncio
async def test_search_rest_retry_on_500(monkeypatch):
    session = GLPISession(
        "http://example.com/apirest.php",
        Credentials(app_token="app", user_token="tok"),
    )

    calls = []

    async def fake_request(method, url, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            return DummyCM(DummyResponse(500, {"message": "err"}))
        return DummyCM(DummyResponse(200, {"data": []}))

    monkeypatch.setattr(
        "backend.adapters.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    with patch("asyncio.sleep", new=AsyncMock()):
        result = await session.search_rest("Ticket")
    assert len(calls) == 2
    assert result == {"data": []}


@pytest.mark.asyncio
async def test_query_graphql_retry_on_429(monkeypatch):
    session = GLPISession(
        "http://example.com/apirest.php",
        Credentials(app_token="app", user_token="tok"),
    )

    call_count = 0

    async def fake_request(method, url, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return DummyCM(DummyResponse(429, {"message": "rate"}))
        return DummyCM(DummyResponse(200, {"data": {"ok": True}}))

    monkeypatch.setattr(
        "backend.adapters.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    with patch("asyncio.sleep", new=AsyncMock()):
        data = await session.query_graphql("query {}", {"x": 1})
    assert call_count == 2
    assert data == {"ok": True}


@pytest.mark.asyncio
async def test_get_all_paginated(monkeypatch):
    session = GLPISession(
        "http://example.com/apirest.php", Credentials(app_token="app", user_token="tok")
    )

    ranges = ["0-1", "2-3", "4-5"]
    responses = [
        DummyResponse(200, {"data": [{"id": 1}, {"id": 2}]}),
        DummyResponse(200, {"data": [{"id": 3}]}),
        DummyResponse(200, {"data": []}),
    ]
    call_count = 0

    async def fake_request(method, url, **kwargs):
        nonlocal call_count
        assert kwargs["params"]["range"] == ranges[call_count]
        resp = responses[call_count]
        call_count += 1
        return DummyCM(resp)

    monkeypatch.setattr(
        "backend.adapters.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    with patch("asyncio.sleep", new=AsyncMock()):
        data = await index_all_paginated("Ticket", page_size=2)

    assert call_count == 3
    assert data == [{"id": 1}, {"id": 2}, {"id": 3}]
