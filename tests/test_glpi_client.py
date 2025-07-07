import base64
from unittest.mock import AsyncMock

import aiohttp
import pytest

from glpi_dashboard.services.glpi_session import Credentials, GLPISession


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
async def test_init_session_user_token(mocker):
    mock_session = mocker.patch(
        "glpi_dashboard.services.glpi_session.ClientSession"
    ).return_value
    mock_session.get = AsyncMock(
        return_value=DummyCM(DummyResponse(200, {"session_token": "tok"}))
    )
    mock_session.closed = False

    creds = Credentials(app_token="APP", user_token="USER")
    client = GLPISession("http://example.com/apirest.php", creds)
    await client._refresh_session_token()

    mock_session.get.assert_awaited_once()
    assert client._session_token == "tok"


@pytest.mark.asyncio
async def test_init_session_basic_auth(mocker):
    mock_session = mocker.patch(
        "glpi_dashboard.services.glpi_session.ClientSession"
    ).return_value
    mock_session.get = AsyncMock(
        return_value=DummyCM(DummyResponse(200, {"session_token": "tok"}))
    )
    mock_session.closed = False

    client = GLPISession("http://example.com/apirest.php", Credentials(app_token="APP"))
    await client._refresh_session_token()

    token = base64.b64encode(b"alice:secret").decode()
    args, kwargs = mock_session.get.call_args
    assert kwargs["headers"]["Authorization"] in {"user_token USER", f"Basic {token}"}
    assert client._session_token == "tok"


@pytest.mark.asyncio
async def test_search_rest_url(mocker):
    mock_session = mocker.patch(
        "glpi_dashboard.services.glpi_session.ClientSession"
    ).return_value

    async def fake_request(method, url, **kwargs):
        return DummyCM(DummyResponse(200, {"data": []}))

    mock_session.request = AsyncMock(side_effect=fake_request)
    mock_session.closed = False

    client = GLPISession("http://example.com/apirest.php", Credentials(app_token="APP"))
    data = await client.search_rest("Ticket", params={"a": 1})

    mock_session.request.assert_awaited_once()
    args, kwargs = mock_session.request.call_args
    assert args[0] == "GET" and args[1].endswith("search/Ticket")
    assert kwargs["params"] == {"a": 1}
    assert data == {"data": []}


@pytest.mark.asyncio
async def test_query_graphql_payload(mocker):
    mock_session = mocker.patch(
        "glpi_dashboard.services.glpi_session.ClientSession"
    ).return_value

    mock_session.request = AsyncMock(
        return_value=DummyCM(DummyResponse(200, {"data": {"ok": True}}))
    )
    mock_session.closed = False

    client = GLPISession("http://example.com/apirest.php", Credentials(app_token="APP"))
    result = await client.query_graphql("query { ping }", {"x": 1})

    mock_session.request.assert_awaited_once()
    args, kwargs = mock_session.request.call_args
    assert args[0] == "POST" and args[1].endswith("graphql")
    assert kwargs["json"] == {"query": "query { ping }", "variables": {"x": 1}}
    assert result == {"ok": True}
