import base64
import httpx
import pytest

from glpi_dashboard.services.glpi_rest_client import GLPIClient


@pytest.mark.asyncio
async def test_init_session_user_token(mocker):
    """
    Testa se GLPIClient.init_session realiza GET em initSession com autenticação por user_token.
    """
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.get = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"session_token": "tok"})
    )
    http_client.headers = {}

    client = GLPIClient(
        "http://example.com/apirest.php", app_token="APP", user_token="USER"
    )
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
    """
    Testa se username/password geram o header Basic Auth corretamente.
    """
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
    """
    Testa se search_rest chama o endpoint correto com os parâmetros esperados.
    """
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.request = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"data": []})
    )

    client = GLPIClient(
        "http://example.com/apirest.php", app_token="APP", user_token="USER"
    )
    data = await client.search_rest("Ticket", params={"a": 1})

    http_client.request.assert_awaited_once_with(
        "GET", "search/Ticket", params={"a": 1}
    )
    assert data == {"data": []}


@pytest.mark.asyncio
async def test_query_graphql_payload(mocker):
    """
    Testa se query_graphql faz POST para /graphql com o payload JSON correto.
    """
    async_client = mocker.patch(
        "glpi_dashboard.services.glpi_rest_client.httpx.AsyncClient"
    )
    http_client = async_client.return_value
    http_client.request = mocker.AsyncMock(
        return_value=httpx.Response(200, json={"data": {"ok": True}})
    )

    client = GLPIClient(
        "http://example.com/apirest.php", app_token="APP", user_token="USER"
    )
    result = await client.query_graphql("query { ping }", {"x": 1})

    http_client.request.assert_awaited_once_with(
        "POST",
        "graphql",
        json={"query": "query { ping }", "variables": {"x": 1}},
    )
    assert result == {"ok": True}
