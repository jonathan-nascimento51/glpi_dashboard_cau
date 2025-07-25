from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from backend.infrastructure.glpi.glpi_session import (
    Credentials,
    GLPISession,
    index_all_paginated,
)

pytest.importorskip("aiohttp")


class DummyCM:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyResponse:
    def __init__(self, status: int, data: Optional[Any] = None):
        self.status = status
        self._data = data if data is not None else {}
        self.headers: dict[str, str] = {}
        # Add attributes required by ClientResponseError for more realistic mocking
        self.request_info = MagicMock()
        self.history = ()

    async def json(self) -> Any:
        return self._data

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                self.request_info,
                self.history,
                status=self.status,
                message="Simulated HTTP Error",
            )


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
        "backend.infrastructure.glpi.glpi_session.ClientSession.request",
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
        "backend.infrastructure.glpi.glpi_session.ClientSession.request",
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
        "backend.infrastructure.glpi.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    with patch("asyncio.sleep", new=AsyncMock()):
        data = await session.query_graphql("query {}", {"x": 1})
    assert call_count == 2
    assert data == {"ok": True}


@pytest.mark.asyncio
async def test_get_all_paginated(monkeypatch):
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
        "backend.infrastructure.glpi.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    with patch("asyncio.sleep", new=AsyncMock()):
        data = await index_all_paginated("Ticket", page_size=2)

    assert call_count == 3
    assert data == [{"id": 1}, {"id": 2}, {"id": 3}]


@pytest.mark.asyncio
async def test_get_all_paginated_content_range(monkeypatch):
    """Stop pagination early when Content-Range provides total count."""

    ranges = ["0-1", "2-3"]
    responses = [
        DummyResponse(200, {"data": [{"id": 1}, {"id": 2}]}),
        DummyResponse(200, {"data": [{"id": 3}]}),
    ]
    responses[0].headers["Content-Range"] = "0-1/3"
    responses[1].headers["Content-Range"] = "2-2/3"
    call_count = 0

    async def fake_request(method, url, **kwargs):
        nonlocal call_count
        assert kwargs["params"]["range"] == ranges[call_count]
        resp = responses[call_count]
        call_count += 1
        return DummyCM(resp)

    monkeypatch.setattr(
        "backend.infrastructure.glpi.glpi_session.ClientSession.request",
        AsyncMock(side_effect=fake_request),
    )
    with patch("asyncio.sleep", new=AsyncMock()):
        data = await index_all_paginated("Ticket", page_size=2)

    assert call_count == 2
    assert data == [{"id": 1}, {"id": 2}, {"id": 3}]


@pytest.mark.asyncio
async def test_api_client_get_all_paginated(monkeypatch):
    from backend.application.glpi_api_client import GlpiApiClient

    ranges = ["0-1", "2-3", "4-5"]
    responses = [
        DummyResponse(200, {"data": [{"id": 1}, {"id": 2}]}),
        DummyResponse(200, {"data": [{"id": 3}]}),
        DummyResponse(200, {"data": []}),
    ]
    call_count = 0

    async def fake_get(endpoint, *, params=None, headers=None, return_headers=False):
        nonlocal call_count
        assert params["range"] == ranges[call_count]
        resp = responses[call_count]
        call_count += 1
        return resp._data, resp.headers

    monkeypatch.setattr(
        "backend.application.glpi_api_client.MappingService",
        lambda *a, **k: MagicMock(initialize=AsyncMock()),
    )
    monkeypatch.setattr(
        "backend.application.glpi_api_client.TicketTranslator", MagicMock
    )

    client = GlpiApiClient(session=MagicMock())
    monkeypatch.setattr(client, "get", AsyncMock(side_effect=fake_get))
    with patch("asyncio.sleep", new=AsyncMock()):
        data = await client.get_all_paginated("Ticket", page_size=2)

    assert call_count == 3
    assert data == [{"id": 1}, {"id": 2}, {"id": 3}]
