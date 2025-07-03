import httpx
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from glpi_dashboard.services.glpi_rest_client import GLPIClient  # noqa: E402
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_list_search_options(monkeypatch):
    client = GLPIClient(
        "http://example.com/apirest.php", app_token="app", user_token="tok"
    )

    async def fake_request(method, url, **kwargs):
        assert method == "GET"
        assert url == "listSearchOptions/Ticket"
        return httpx.Response(200, json={"1": {"name": "ID", "datatype": "int"}})

    monkeypatch.setattr(client._client, "request", fake_request)

    data = await client.list_search_options("Ticket")
    assert data["1"]["name"] == "ID"


@pytest.mark.asyncio
async def test_search_rest_retry_on_500(monkeypatch):
    client = GLPIClient(
        "http://example.com/apirest.php",
        app_token="app",
        user_token="tok",
        retry_max=2,
        retry_base_delay=0.0,
    )

    calls: list[int] = []

    async def fake_request(method, url, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(500, json={"message": "err"})
        return httpx.Response(200, json={"data": []})

    monkeypatch.setattr(client._client, "request", fake_request)
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        result = await client.search_rest("Ticket")
    assert len(calls) == 2
    assert result == {"data": []}
    assert sleep_mock.call_count == 1


@pytest.mark.asyncio
async def test_query_graphql_retry_on_429(monkeypatch):
    client = GLPIClient(
        "http://example.com/apirest.php",
        app_token="app",
        user_token="tok",
        retry_max=1,
        retry_base_delay=0.0,
    )

    call_count = 0

    async def fake_request(method, url, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(429, json={"message": "rate"})
        return httpx.Response(200, json={"data": {"ok": True}})

    monkeypatch.setattr(client._client, "request", fake_request)
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        data = await client.query_graphql("query {}", {"x": 1})
    assert call_count == 2
    assert data == {"ok": True}
    assert sleep_mock.call_count == 1
