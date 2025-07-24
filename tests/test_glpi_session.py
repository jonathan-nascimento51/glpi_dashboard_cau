import asyncio as aio
import json
import os
import ssl
from contextlib import asynccontextmanager
from typing import Optional
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("aiohttp")

import aiohttp  # noqa: E402
from aiohttp import BasicAuth  # noqa: E402
from backend.infrastructure.glpi import glpi_session  # noqa: E402
from backend.infrastructure.glpi.glpi_session import (  # noqa: E402
    Credentials,
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GLPIInternalServerError,
    GLPINotFoundError,
    GLPISession,
    GLPITooManyRequestsError,
    GLPIUnauthorizedError,
)
from shared.utils.logging import init_logging  # noqa: E402

from tests.helpers import make_cm, make_mock_response  # noqa: E402

pytest.importorskip(
    "aiohttp", reason="aiohttp package is required to run glpi_session tests"
)


@pytest.fixture(autouse=True)
def _configure_logging() -> None:
    """Ensure logging is configured for tests."""
    init_logging()


@pytest.fixture
def base_url() -> str:
    """Fixture for the base GLPI API URL."""
    return "https://glpi.company.com/apirest.php"


@pytest.fixture
def app_token() -> str:
    """Fixture for the GLPI App-Token."""
    return "test_app_token"


@pytest.fixture
def user_token() -> str:
    """Fixture for a GLPI user token."""
    return "test_user_token_123"


@pytest.fixture
def username() -> str:
    """Fixture for a GLPI username."""
    return "test_user"


@pytest.fixture
def password() -> str:
    """Fixture for a GLPI password."""
    return "test_password"


@pytest.fixture
def mock_response():
    """Return the ``make_mock_response`` helper for convenience."""

    def _factory(
        status: int,
        json_data: Optional[dict[str, object]] = None,
        raise_for_status_exc: bool = False,
    ):
        return make_mock_response(status, json_data, raise_for_status_exc)

    return _factory


class _FakeMethod:
    """Replicate an aiohttp HTTP method for testing."""

    def __init__(self) -> None:
        self._mock = MagicMock()
        self.side_effect = None

    def _resolve_effect(self, args, kwargs):
        effect = self.side_effect
        if isinstance(effect, list):
            effect = effect.pop(0) if effect else None
        return effect(*args, **kwargs) if callable(effect) else effect

    def __call__(self, *args, **kwargs):
        self._mock(*args, **kwargs)
        result = self._resolve_effect(args, kwargs)
        if result is None:
            result = make_mock_response(200, {})
        if hasattr(result, "__aenter__"):
            return result

        @asynccontextmanager
        async def cm():
            yield result

        return cm()

    def __getattr__(self, item):
        return getattr(self._mock, item)


class FakeClientSession(MagicMock):
    """Minimal ``aiohttp.ClientSession`` replacement for tests."""

    def __init__(self) -> None:
        super().__init__(spec=aiohttp.ClientSession)
        self.closed = False
        self.get = _FakeMethod()
        self.post = _FakeMethod()
        self.put = _FakeMethod()
        self.delete = _FakeMethod()
        self.request = _FakeMethod()

    async def close(self) -> None:
        self.closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    @property
    def call_count(self) -> int:  # type: ignore[override]
        return (
            self.get.call_count
            + self.post.call_count
            + self.put.call_count
            + self.delete.call_count
            + self.request.call_count
        )

    def assert_not_called(self) -> None:  # type: ignore[override]
        if self.call_count != 0:
            raise AssertionError("Expected no HTTP calls, but some were made")


@pytest.fixture
def mock_client_session(mock_response):
    """Patch ``aiohttp.ClientSession`` to return a ``FakeClientSession``."""

    session_instance = FakeClientSession()
    with (
        patch(
            "backend.infrastructure.glpi.glpi_session.ClientSession",
            return_value=session_instance,
        ),
        patch("aiohttp.ClientSession", return_value=session_instance),
    ):
        yield session_instance


def test_credentials_require_auth(app_token):
    """Credentials without user_token or username/password should raise."""
    with pytest.raises(ValueError):
        Credentials(app_token=app_token)


def test_credentials_prioritize_user_token(app_token):
    """If both auth methods are provided, user_token wins."""
    creds = Credentials(
        app_token=app_token,
        user_token="tok",
        username="user",
        password="pw",
    )
    assert creds.user_token == "tok"
    assert creds.username is None
    assert creds.password is None


@pytest.mark.asyncio
async def test_glpi_session_context_manager_user_token_auth(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """
    Tests the GLPISession context manager when authenticating with a user token.
    Verifies session initiation, token storage, and graceful exit.
    """
    os.environ.pop("HTTP_PROXY", None)
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    # Mock the initSession call for user_token via GET with headers
    mock_client_session.get.side_effect = lambda *a, **k: make_cm(
        200, {"session_token": user_token}
    )

    async with glpi_session as session:
        assert session._session_token == user_token
        # Verify initSession was called with the user_token in the payload
        mock_client_session.get.assert_called_once_with(
            f"{base_url}/initSession",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Authorization": f"user_token {user_token}",
            },
            proxy=ANY,
            timeout=ANY,
        )
        assert session._session is not None
        assert not session._session.closed
        assert (
            session._refresh_task is None
        )  # Proactive refresh should not start for user_token

    assert session._session_token is None
    assert session._session.closed
    # When using user_token authentication, killSession should not be called
    assert mock_client_session.call_count == 1


@pytest.mark.asyncio
async def test_glpi_session_context_manager_username_password_auth(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """
    Tests the GLPISession context manager when authenticating with username/password.
    Verifies session initiation, token storage, and graceful exit.
    """
    os.environ.pop("HTTP_PROXY", None)
    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(base_url, credentials)

    # Mock the initSession call for username/password using GET with Basic Auth
    mock_client_session.return_value = mock_response(
        200, {"session_token": "initial_session_token"}
    )

    async with glpi_session as session:
        assert session._session_token == "initial_session_token"
        # Verify initSession was called with username/password in the payload
        mock_client_session.get.assert_called_once_with(
            f"{base_url}/initSession",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Authorization": BasicAuth(username, password).encode(),
            },
            proxy=ANY,
            timeout=ANY,
        )
        assert session._session is not None
        assert not session._session.closed
        assert session._refresh_task is not None  # Proactive refresh should start

    assert glpi_session._session_token is None
    assert session._session.closed
    # Verify killSession was called with the correct headers as the last call
    kill_call = mock_client_session.get.call_args_list[-1]
    assert kill_call.args[0] == f"{base_url}/killSession"
    assert kill_call.kwargs["headers"] == {
        "Content-Type": "application/json",
        "Session-Token": "initial_session_token",
        "App-Token": app_token,
    }


@pytest.mark.asyncio
async def test_get_request_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Tests a successful GET request through the GLPISession."""
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    mock_client_session.return_value = mock_response(
        200, {"session_token": user_token}
    )  # Mock initSession
    mock_client_session.request.return_value = mock_response(
        200, {"data": "ticket_info"}
    )

    async with glpi_session as session:
        response_data = await session.get("Ticket/123")
        assert response_data == {"data": "ticket_info"}
        mock_client_session.request.assert_called_once_with(
            "GET",
            f"{base_url}/Ticket/123",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Session-Token": user_token,
            },
            json=None,
            params=None,
            proxy=ANY,
            timeout=ANY,
        )


@pytest.mark.asyncio
async def test_post_request_success(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """Tests a successful POST request through the GLPISession."""
    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(base_url, credentials)

    # Mock initSession call and then the actual POST request
    mock_client_session.return_value = mock_response(
        200, {"session_token": "initial_session_token"}
    )
    mock_client_session.request.return_value = mock_response(
        201, {"id": 1}
    )  # For actual POST request

    async with glpi_session as session:
        payload = {"name": "New Ticket", "content": "Issue description"}
        response_data = await session.post("Ticket/", json_data=payload)
        assert response_data == {"id": 1}
        mock_client_session.request.assert_called_once_with(
            "POST",
            f"{base_url}/Ticket/",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Session-Token": "initial_session_token",
            },
            json=payload,
            params=None,
            proxy=ANY,
            timeout=ANY,
        )


@pytest.mark.asyncio
async def test_put_request_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Tests a successful PUT request through the GLPISession."""
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    mock_client_session.return_value = mock_response(
        200, {"session_token": user_token}
    )  # Mock initSession
    mock_client_session.request.return_value = mock_response(
        200, {"message": "updated"}
    )

    async with glpi_session as session:
        payload = {"id": 123, "name": "Updated Ticket"}
        response_data = await session.put("Ticket/123", json_data=payload)
        assert response_data == {"message": "updated"}
        mock_client_session.request.assert_called_once_with(
            "PUT",
            f"{base_url}/Ticket/123",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Session-Token": user_token,
            },
            json=payload,
            params=None,
            proxy=ANY,
            timeout=ANY,
        )


@pytest.mark.asyncio
async def test_delete_request_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Tests a successful DELETE request through the GLPISession."""
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    mock_client_session.return_value = mock_response(
        200, {"session_token": user_token}
    )  # Mock initSession
    mock_client_session.request.return_value = mock_response(
        200, {"message": "deleted"}
    )

    async with glpi_session as session:
        response_data = await session.delete("Ticket/123")
        assert response_data == {"message": "deleted"}
        mock_client_session.request.assert_called_once_with(
            "DELETE",
            f"{base_url}/Ticket/123",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Session-Token": user_token,
            },
            json=None,
            params=None,
            proxy=ANY,
            timeout=ANY,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_exception",
    [
        (400, GLPIBadRequestError),
        (401, GLPIUnauthorizedError),
        (403, GLPIForbiddenError),
        (404, GLPINotFoundError),
        (429, GLPITooManyRequestsError),
        (500, GLPIInternalServerError),
    ],
)
async def test_api_error_handling(
    base_url,
    app_token,
    user_token,
    mock_client_session,
    mock_response,
    status_code,
    expected_exception,
):
    """
    Tests that custom exceptions are raised for various HTTP error status codes.
    """
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    mock_client_session.return_value = mock_response(
        200, {"session_token": user_token}
    )  # Mock initSession
    mock_client_session.request.return_value = mock_response(
        status_code, {"error": "test error"}, raise_for_status_exc=True
    )

    async with glpi_session as session:
        with pytest.raises(expected_exception) as excinfo:
            await session.get("some_endpoint")
        assert excinfo.value.status_code == status_code
        assert "test error" in str(excinfo.value)
        assert excinfo.value.response_data == {"error": "test error"}


@pytest.mark.asyncio
async def test_session_refresh_on_401_success(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """
    Tests automatic session token refresh when a 401 Unauthorized error occurs,
    followed by a successful retry.
    """
    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(base_url, credentials)

    # Configure side_effect for mock_client_index:
    # 1. Initial initSession call (from __aenter__)
    # 2. Second initSession call (for refresh after 401)
    mock_client_session.side_effect = [
        make_cm(200, {"session_token": "expired_session_token"}),
        make_cm(200, {"session_token": "refreshed_session_token"}),
        make_cm(200, {}),
    ]

    # Configure side_effect for mock_client_session.request:
    # 1. First request attempt gets 401
    # 2. Second request attempt (after refresh) gets 200
    mock_client_session.request.side_effect = [
        make_cm(401, {"error": "Unauthorized"}, True),
        make_cm(200, {"data": "refreshed_data"}),
    ]

    async with glpi_session as session:
        # Verify initial session token
        assert session._session_token == "expired_session_token"

        response_data = await session.get("Ticket/123")
        assert response_data == {"data": "refreshed_data"}
        assert session._session_token == "refreshed_session_token"

        # Check call counts:
        # 1. Initial initSession (from __aenter__)
        # 2. First request (401)
        # 3. Refresh initSession (triggered by 401)
        # 4. Second request (successful)
        assert mock_client_session.request.call_count == 2

        # Verify the first request used the expired token
        first_request_call = mock_client_session.request.call_args_list[0]
        assert (
            first_request_call.kwargs["headers"]["Session-Token"]
            == "expired_session_token"
        )

        # Verify the second request used the refreshed token
        second_request_call = mock_client_session.request.call_args_list[1]
        assert (
            second_request_call.kwargs["headers"]["Session-Token"]
            == "refreshed_session_token"
        )

    # After exiting the context, killSession is called
    assert mock_client_session.call_count == 3


@pytest.mark.asyncio
async def test_session_refresh_on_401_failure(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """
    Tests that a GLPIUnauthorizedError is raised if session refresh fails after a 401.
    """
    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(base_url, credentials)

    # Initial initSession call succeeds, but refresh attempt fails
    mock_client_session.side_effect = [
        make_cm(200, {"session_token": "expired_session_token"}),
        make_cm(401, {"error": "Unauthorized"}, True),
        make_cm(200, {}),
    ]

    # First request attempt gets 401
    mock_client_session.request.return_value = mock_response(
        401, {"error": "Unauthorized"}, raise_for_status_exc=True
    )

    async with glpi_session as session:
        with pytest.raises(GLPIUnauthorizedError) as excinfo:
            await session.get("Ticket/123")
        assert "failed to authenticate after multiple retries" in str(excinfo.value)
        assert excinfo.value.status_code == 401
        assert (
            mock_client_session.request.call_count == 1
        )  # Only one request attempt before giving up

    assert mock_client_session.call_count == 3  # init, refresh, killSession


@pytest.mark.asyncio
async def test_proactive_refresh_loop_username_password(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """
    Tests the proactive session refresh loop for username/password authentication.
    Uses a short refresh_interval for testing purposes.
    """
    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(
        base_url,
        credentials,
        refresh_interval=0.2,  # type: ignore
    )  # Set a short interval

    # Mock initSession for initial and subsequent proactive refreshes
    mock_client_session.side_effect = [
        make_cm(200, {"session_token": "initial_token"}),
        make_cm(200, {"session_token": "proactive_token_1"}),
        make_cm(200, {"session_token": "proactive_token_2"}),
        make_cm(200, {}),
    ]

    async with glpi_session as session:
        assert session._session_token == "initial_token"
        await aio.sleep(0.25)  # Wait for first proactive refresh
        assert session._session_token != "initial_token"
        await aio.sleep(0.25)  # Wait for second proactive refresh
        assert session._session_token == "proactive_token_2"

    # Check that get was called for init + two refreshes + killSession
    assert mock_client_session.call_count == 4


@pytest.mark.asyncio
async def test_kill_session_no_token(base_url, app_token, mock_client_session):
    """_kill_session should do nothing if no token is set."""
    creds = Credentials(app_token=app_token, user_token="tok")
    session = GLPISession(base_url, creds)
    session._session = mock_client_session
    session._session_token = None
    await session._kill_session()
    mock_client_session.assert_not_called()


@pytest.mark.asyncio
async def test_kill_session_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """_kill_session should call the endpoint and clear the token."""
    creds = Credentials(app_token=app_token, user_token=user_token)
    session = GLPISession(base_url, creds)
    session._session = mock_client_session
    session._session_token = user_token
    mock_client_session.return_value = mock_response(200, {})
    await session._kill_session()
    mock_client_session.get.assert_called_once_with(
        f"{base_url}/killSession",
        headers={
            "Content-Type": "application/json",
            "Session-Token": user_token,
            "App-Token": app_token,
        },
        proxy=ANY,
        timeout=ANY,
    )
    assert session._session_token is None


@pytest.mark.asyncio
async def test_aexit_suppresses_cancellation(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """Cancellation of the refresh loop should not propagate errors."""

    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(base_url, credentials, refresh_interval=3600)

    mock_client_session.get.return_value = make_cm(200, {})

    async def sleep_forever() -> None:
        await aio.sleep(10)

    async def fake_refresh():
        glpi_session._session_token = "tok"

    with (
        patch.object(glpi_session, "_proactive_refresh_loop", sleep_forever),
        patch.object(
            glpi_session,
            "_refresh_session_token",
            new=AsyncMock(side_effect=fake_refresh),
        ),
    ):
        async with glpi_session as session:
            assert session._refresh_task is not None

    assert glpi_session._session_token is None
    assert glpi_session._session is not None and glpi_session._session.closed
    assert glpi_session._refresh_task is not None and glpi_session._refresh_task.done()


@pytest.mark.asyncio
async def test_request_network_error(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Network errors trigger retries and eventually succeed."""

    creds = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, creds)

    # initSession succeeds
    mock_client_session.get.side_effect = lambda *a, **k: make_cm(
        200, {"session_token": user_token}
    )

    err = aiohttp.ClientConnectionError("fail")

    def side_effect(*args, **kwargs):
        if side_effect.calls < 2:  # type: ignore[attr-defined]
            side_effect.calls += 1  # type: ignore[attr-defined]
            raise err
        return mock_response(200, {"data": {"id": 1}})

    side_effect.calls = 0  # type: ignore[attr-defined]
    mock_client_session.request.side_effect = side_effect

    with patch("asyncio.sleep", new=AsyncMock()):
        async with glpi_session as session:
            with pytest.raises(GLPIAPIError):
                await session.get("Ticket/1")

    assert mock_client_session.request.call_count == 1


@pytest.mark.asyncio
async def test_verify_ssl_disabled_passes_ssl_false(
    base_url, app_token, user_token, mock_response
):
    with (
        patch("backend.infrastructure.glpi.glpi_session.ClientSession") as session_cls,
        patch("aiohttp.ClientSession") as aiohttp_session_cls,
        patch("backend.infrastructure.glpi.glpi_session.TCPConnector") as connector_cls,
    ):
        session_instance = MagicMock()
        session_instance.closed = False
        session_instance.close = AsyncMock()

        @asynccontextmanager
        async def default_ctx():
            yield mock_response(200, {"session_token": user_token})

        session_instance.get = MagicMock(return_value=default_ctx())
        session_instance.request = MagicMock(return_value=default_ctx())
        session_instance.__aenter__ = AsyncMock(return_value=session_instance)
        session_instance.__aexit__ = AsyncMock(return_value=None)
        session_cls.return_value = session_instance
        aiohttp_session_cls.return_value = session_instance
        connector_cls.return_value = MagicMock()

        creds = Credentials(app_token=app_token, user_token=user_token)
        glpi_session = GLPISession(base_url, creds, verify_ssl=False)
        async with glpi_session as session:
            await session.get("Ticket/1")

        connector_cls.assert_called_with(ssl=False)
        session_instance.get.assert_any_call(
            f"{base_url}/initSession",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Authorization": f"user_token {user_token}",
            },
            proxy=ANY,
            timeout=ANY,
            ssl=ANY,
        )
        session_instance.request.assert_called_with(
            "GET",
            f"{base_url}/Ticket/1",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Session-Token": user_token,
            },
            json=None,
            params=None,
            proxy=ANY,
            timeout=ANY,
            ssl=False,
        )


@pytest.mark.asyncio
async def test_custom_ssl_context_passed_through(
    base_url, app_token, user_token, mock_response
):
    ctx = ssl.create_default_context()
    with (
        patch("backend.infrastructure.glpi.glpi_session.ClientSession") as session_cls,
        patch("aiohttp.ClientSession") as aiohttp_session_cls,
        patch("backend.infrastructure.glpi.glpi_session.TCPConnector") as connector_cls,
    ):
        session_instance = MagicMock()
        session_instance.closed = False
        session_instance.close = AsyncMock()

        @asynccontextmanager
        async def default_ctx():
            yield mock_response(200, {"session_token": user_token})

        session_instance.get = MagicMock(return_value=default_ctx())
        session_instance.request = MagicMock(return_value=default_ctx())
        session_instance.__aenter__ = AsyncMock(return_value=session_instance)
        session_instance.__aexit__ = AsyncMock(return_value=None)
        session_cls.return_value = session_instance
        aiohttp_session_cls.return_value = session_instance
        connector_cls.return_value = MagicMock()

        creds = Credentials(app_token=app_token, user_token=user_token)
        glpi_session = GLPISession(base_url, creds, ssl_context=ctx)
        async with glpi_session as session:
            await session.get("Ticket/1")

        connector_cls.assert_called_with(ssl=ctx)
        session_instance.get.assert_any_call(
            f"{base_url}/initSession",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Authorization": f"user_token {user_token}",
            },
            proxy=ANY,
            timeout=ANY,
            ssl=ctx,
        )
        session_instance.request.assert_called_with(
            "GET",
            f"{base_url}/Ticket/1",
            headers={
                "Content-Type": "application/json",
                "App-Token": app_token,
                "Session-Token": user_token,
            },
            json=None,
            params=None,
            proxy=ANY,
            timeout=ANY,
            ssl=ctx,
        )


@pytest.mark.asyncio
async def test_open_session_tool_error(monkeypatch):
    class BadSession:
        async def __aenter__(self):
            raise RuntimeError("boom")

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(glpi_session, "GLPISession", lambda *a, **k: BadSession())
    creds = glpi_session.Credentials(app_token="a", user_token="u")
    params = glpi_session.SessionParams(base_url="http://x", credentials=creds)
    out = await glpi_session.open_session_tool(params)
    data = json.loads(out)
    assert data["error"]["details"] == "boom"


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_request_retries_on_server_error_success(
    base_url,
    app_token,
    user_token,
    mock_client_session,
    mock_response,
):
    """Retries on 5xx errors and eventually returns the response."""
    creds = Credentials(app_token=app_token, user_token=user_token)
    session = GLPISession(base_url, creds)

    mock_client_session.get.return_value = mock_response(
        200, {"session_token": user_token}
    )
    mock_client_session.request.side_effect = [
        mock_response(500, {"error": "boom"}, raise_for_status_exc=True),
        mock_response(503, {"error": "down"}, raise_for_status_exc=True),
        mock_response(200, {"ok": True}),
    ]

    with patch("asyncio.sleep", new=AsyncMock()):
        async with session as glpi:
            data = await glpi.get("Ticket/1")
            assert data == {"ok": True}

    assert mock_client_session.request.call_count == 3


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_consecutive_failures(
    base_url,
    app_token,
    user_token,
    mock_client_session,
    mock_response,
):
    """Circuit breaker opens after repeated server errors."""
    pytest.importorskip("pybreaker")
    import pybreaker
    from shared.utils.resilience import breaker

    # Reset breaker state for this test to ensure it's closed.
    breaker.close()

    creds = Credentials(app_token=app_token, user_token=user_token)
    session = GLPISession(base_url, creds)

    mock_client_session.get.side_effect = lambda *a, **k: make_cm(
        200, {"session_token": user_token}
    )
    # The decorated `_request` method will be called. We need it to fail
    # consistently to trigger the breaker. Let's provide enough failing responses.
    # The number of failures needed depends on `breaker.fail_max` and any
    # retries from the decorator. We'll provide plenty.
    mock_client_session.request.side_effect = [
        mock_response(500, {"error": "boom"}, raise_for_status_exc=True)
    ] * 20  # Provide more than enough failing responses

    with patch("asyncio.sleep", new=AsyncMock()):
        async with session as glpi:
            # Loop up to the breaker's failure threshold.
            for _ in range(breaker.fail_max):
                with pytest.raises(GLPIInternalServerError):
                    # Call the method directly. The resilience logic is handled
                    # by the @retry_api_call decorator on the _request method.
                    await glpi.get("Ticket/1")

    # After `fail_max` consecutive failures, the breaker should be open.
    assert breaker.current_state == pybreaker.STATE_OPEN
    # Clean up for subsequent tests.
    breaker.close()


@pytest.mark.asyncio
async def test_get_full_session_success(base_url, app_token, user_token):
    """get_full_session should return session details."""

    creds = Credentials(app_token=app_token, user_token=user_token)
    glpi = GLPISession(base_url, creds)
    glpi._session_token = user_token

    with patch.object(
        glpi,
        "get",
        AsyncMock(return_value={"session": "info"}),
    ) as mock_get:
        data = await glpi.get_full_session()
        assert data == {"session": "info"}
        mock_get.assert_awaited_once_with(
            "getFullSession",
            headers={
                "Session-Token": user_token,
                "App-Token": app_token,
            },
        )


@pytest.mark.asyncio
async def test_get_full_session_error(base_url, app_token, user_token):
    """get_full_session should raise mapped errors."""

    creds = Credentials(app_token=app_token, user_token=user_token)
    glpi = GLPISession(base_url, creds)
    glpi._session_token = user_token

    with patch.object(
        glpi,
        "get",
        AsyncMock(side_effect=GLPIForbiddenError(403, "no")),
    ):
        with pytest.raises(GLPIForbiddenError):
            await glpi.get_full_session()
