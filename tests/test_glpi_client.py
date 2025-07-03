import os
import sys
import base64

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))  # noqa: E402

from glpi_dashboard.services.glpi_rest_client import GLPIClient  # noqa: E402


@pytest.mark.asyncio
async def test_init_session_user_token(mocker):
    """GLPIClient.init_session should GET initSession with token auth."""
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.get = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"session_token": "tok"})
    )
    http_client.headers = {}
    http_client.headers = {}

    client = GLPIClient("http://example.com/apirest.php", app_token="APP", user_token="USER")
    await client.init_session()

    async_client.assert_called_once_with(
        base_url="http://example.com/apirest.php",
        timeout=30.0,
        verify=True,
        headers={"App-Token": "APP"},
    )
    http_client.get.assert_awaited_once_with(
        "initSession",
        headers={"App-Token": "APP", "Authorization": "user_token USER"},
    )
    assert client._session_token == "tok"
    assert http_client.headers["Session-Token"] == "tok"


@pytest.mark.asyncio
async def test_init_session_basic_auth(mocker):
    """Username/password should generate Basic auth header."""
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.get = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"session_token": "tok"})
    )

    client = GLPIClient("http://example.com/apirest.php", app_token="APP")
    await client.init_session(username="alice", password="secret")

    token = base64.b64encode(b"alice:secret").decode()
    http_client.get.assert_awaited_once_with(
        "initSession",
        headers={"App-Token": "APP", "Authorization": f"Basic {token}"},
    )
    assert client._session_token == "tok"


@pytest.mark.asyncio
async def test_search_rest_url(mocker):
    """search_rest should call the correct endpoint with params."""
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.request = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"data": []})
    )

    client = GLPIClient("http://example.com/apirest.php", app_token="APP", user_token="USER")
    data = await client.search_rest("Ticket", params={"a": 1})

    http_client.request.assert_awaited_once_with(
        "GET", "search/Ticket", params={"a": 1}
    )
    assert data == {"data": []}


@pytest.mark.asyncio
async def test_query_graphql_payload(mocker):
    """query_graphql should POST to /graphql with proper JSON."""
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.request = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"data": {"ok": True}})
    )

    client = GLPIClient("http://example.com/apirest.php", app_token="APP", user_token="USER")
    result = await client.query_graphql("query { ping }", {"x": 1})

    http_client.request.assert_awaited_once_with(
        "POST",
        "graphql",
        json={"query": "query { ping }", "variables": {"x": 1}},
    )
    assert result == {"ok": True}
