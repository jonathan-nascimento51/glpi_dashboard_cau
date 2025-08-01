from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import BasicAuth

from backend.infrastructure.glpi import glpi_client_logging
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession

pytest.importorskip("aiohttp")


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
        # Adiciona atributos para um mock mais realista, consistente com outros testes
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
async def test_init_session_user_token(mocker):
    mock_session = mocker.patch(
        "backend.infrastructure.glpi.glpi_session.aiohttp.ClientSession"
    ).return_value
    mock_index = MagicMock(
        return_value=DummyCM(DummyResponse(200, {"session_token": "tok"}))
    )
    mock_session.closed = False
    mock_session.get = mock_index
    mock_session.get = mock_index

    creds = Credentials(app_token="APP", user_token="USER")
    client = GLPISession("http://example.com/apirest.php", creds)
    await client._refresh_session_token()

    mock_index.assert_called_once()
    assert client._session_token == "tok"


@pytest.mark.asyncio
async def test_init_session_basic_auth(mocker):
    mock_session = mocker.patch(
        "backend.infrastructure.glpi.glpi_session.aiohttp.ClientSession"
    ).return_value
    mock_index = MagicMock(
        return_value=DummyCM(DummyResponse(200, {"session_token": "tok"}))
    )
    mock_session.closed = False
    mock_session.get = mock_index

    client = GLPISession(
        "http://example.com/apirest.php",
        Credentials(app_token="APP", user_token="USER"),
    )
    await client._refresh_session_token()

    token = BasicAuth("alice", "secret").encode()
    args, kwargs = mock_index.call_args
    assert kwargs["headers"]["Authorization"] in {"user_token USER", f"Basic {token}"}
    assert client._session_token == "tok"


@pytest.mark.asyncio
async def test_search_rest_url(mocker):
    mock_session = mocker.patch(
        "backend.infrastructure.glpi.glpi_session.aiohttp.ClientSession"
    ).return_value

    async def fake_request(method, url, **kwargs):
        return DummyCM(DummyResponse(200, {"data": []}))

    mock_session.request = MagicMock(side_effect=fake_request)
    mock_session.closed = False

    client = GLPISession(
        "http://example.com/apirest.php",
        Credentials(app_token="APP", user_token="USER"),
    )
    data = await client.search_rest("Ticket", params={"a": 1})

    mock_session.request.assert_called_once()
    args, kwargs = mock_session.request.call_args
    assert args[0] == "GET" and args[1].endswith("search/Ticket")
    assert kwargs["params"] == {"a": 1}
    assert data == {"data": []}


@pytest.mark.asyncio
async def test_query_graphql_payload(mocker):
    mock_session = mocker.patch(
        "backend.infrastructure.glpi.glpi_session.aiohttp.ClientSession"
    ).return_value

    mock_session.request = MagicMock(
        return_value=DummyCM(DummyResponse(200, {"data": {"ok": True}}))
    )
    mock_session.closed = False

    client = GLPISession(
        "http://example.com/apirest.php",
        Credentials(app_token="APP", user_token="USER"),
    )
    result = await client.query_graphql("query { ping }", {"x": 1})

    mock_session.request.assert_called_once()
    args, kwargs = mock_session.request.call_args
    assert args[0] == "POST" and args[1].endswith("graphql")
    assert kwargs["json"] == {"query": "query { ping }", "variables": {"x": 1}}
    assert result == {"ok": True}


def test_setup_logger_initializes_logging():
    import importlib

    mod = importlib.reload(glpi_client_logging)
    assert not mod.is_logging_configured()

    mod.get_logger("t").info("no config")
    assert not mod.is_logging_configured()

    mod.setup_logger("t")
    assert mod.is_logging_configured()


@pytest.mark.asyncio
async def test_get_ticket_counts_by_level(monkeypatch):
    session = GLPISession(
        "http://example.com/apirest.php",
        Credentials(app_token="APP", user_token="USER"),
    )

    async def fake_get(endpoint, *, params=None, headers=None, return_headers=False):
        # Determine status from params
        status_criteria = [c for c in params["criteria"] if c.get("field") == "status"]
        status_value = int(status_criteria[0]["value"])
        mapping = {1: 2, 4: 1, 5: 3}
        return {"totalcount": mapping.get(status_value, 0)}

    monkeypatch.setattr(session, "get", AsyncMock(side_effect=fake_get))

    counts = await session.get_ticket_counts_by_level("N1")

    assert counts == {"new": 2, "pending": 1, "solved": 3}
