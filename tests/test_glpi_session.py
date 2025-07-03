import os
import sys
import pytest
import asyncio as aio
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from typing import Optional
from contextlib import asynccontextmanager

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

from glpi_dashboard.services.glpi_session import (  # noqa: E402
    GLPISession,
    Credentials,
    GLPIUnauthorizedError,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIInternalServerError,
    GLPIAPIError,
)
import aiohttp  # noqa: E402
from glpi_dashboard.logging_config import setup_logging  # noqa: E402


@pytest.fixture(autouse=True)
def _configure_logging() -> None:
    """Ensure logging is configured for tests."""
    setup_logging()


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
    """
    Fixture to create a mock aiohttp ClientResponse object.
    Allows setting status, JSON data, and simulating raise_for_status() exceptions.
    """

    def _mock_response(
        status: int,
        json_data: Optional[dict] = None,
        raise_for_status_exc: bool = False,
    ):
        mock_resp = MagicMock(spec=aiohttp.ClientResponse)
        mock_resp.status = status
        mock_resp.json = AsyncMock(
            return_value=json_data if json_data is not None else {}
        )
        mock_resp.text = AsyncMock(
            return_value=str(json_data) if json_data is not None else ""
        )
        mock_resp.request_info = MagicMock()  # Required for ClientResponseError
        mock_resp.history = ()  # Required for ClientResponseError

        if raise_for_status_exc:
            err = aiohttp.ClientResponseError(
                request_info=mock_resp.request_info,
                history=mock_resp.history,
                status=status,
                message="Simulated HTTP Error",
            )
            mock_resp.raise_for_status.side_effect = err
        else:
            mock_resp.raise_for_status.return_value = None

        # Mocking async context manager for response
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)
        return mock_resp

    return _mock_response


@pytest.fixture
def mock_client_session(mock_response):
    """
    Fixture to mock aiohttp.ClientSession and its HTTP methods.
    Patches aiohttp.ClientSession globally for tests.
    """
    with patch(
        "glpi_dashboard.services.glpi_session.ClientSession"
    ) as mock_session_cls:
        mock_session_instance = MagicMock()
        mock_session_instance.closed = False  # Assume not closed initially

        @asynccontextmanager
        async def default_post():
            yield mock_response(200, {"session_token": "mock_session_token"})

        @asynccontextmanager
        async def default_request():
            yield mock_response(200, {})

        # Mock HTTP methods to return async context managers
        mock_session_instance.post = MagicMock(return_value=default_post())
        mock_session_instance.get = MagicMock(return_value=default_request())
        mock_session_instance.put = MagicMock(return_value=default_request())
        mock_session_instance.delete = MagicMock(return_value=default_request())
        mock_session_instance.request = MagicMock(return_value=default_request())

        # Mocking async context manager for session
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)

        async def close():
            mock_session_instance.closed = True

        mock_session_instance.close = AsyncMock(side_effect=close)

        mock_session_cls.return_value = mock_session_instance
        yield mock_session_instance


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
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    # Mock the initSession call for user_token via GET with headers
    mock_client_session.get.return_value = mock_response(
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
            proxy=None,
            timeout=ANY,
        )
        assert session._session is not None
        assert not session._session.closed
        assert (
            session._refresh_task is None
        )  # Proactive refresh should not start for user_token

    assert session._session_token is None
    assert session._session.closed
    # Verify killSession was called with the correct headers as the last call
    kill_call = mock_client_session.get.call_args_list[-1]
    assert kill_call.args[0] == f"{base_url}/killSession"
    assert kill_call.kwargs["headers"] == {
        "Content-Type": "application/json",
        "Session-Token": user_token,
        "App-Token": app_token,
    }


@pytest.mark.asyncio
async def test_glpi_session_context_manager_username_password_auth(
    base_url, app_token, username, password, mock_client_session, mock_response
):
    """
    Tests the GLPISession context manager when authenticating with username/password.
    Verifies session initiation, token storage, and graceful exit.
    """
    credentials = Credentials(app_token=app_token, username=username, password=password)
    glpi_session = GLPISession(base_url, credentials)

    # Mock the initSession call for username/password using GET with Basic Auth
    mock_client_session.get.return_value = mock_response(
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
                "Authorization": "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
            },
            proxy=None,
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

    mock_client_session.get.return_value = mock_response(
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
            proxy=None,
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
    mock_client_session.get.return_value = mock_response(
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
            proxy=None,
            timeout=ANY,
        )


@pytest.mark.asyncio
async def test_put_request_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Tests a successful PUT request through the GLPISession."""
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    mock_client_session.get.return_value = mock_response(
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
            proxy=None,
            timeout=ANY,
        )


@pytest.mark.asyncio
async def test_delete_request_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Tests a successful DELETE request through the GLPISession."""
    credentials = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, credentials)

    mock_client_session.get.return_value = mock_response(
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
            proxy=None,
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

    mock_client_session.get.return_value = mock_response(
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

    # Configure side_effect for mock_client_session.get:
    # 1. Initial initSession call (from __aenter__)
    # 2. Second initSession call (for refresh after 401)
    mock_client_session.get.side_effect = [
        mock_response(200, {"session_token": "expired_session_token"}),
        mock_response(200, {"session_token": "refreshed_session_token"}),
        mock_response(200, {}),
    ]

    # Configure side_effect for mock_client_session.request:
    # 1. First request attempt gets 401
    # 2. Second request attempt (after refresh) gets 200
    mock_client_session.request.side_effect = [
        mock_response(401, {"error": "Unauthorized"}, raise_for_status_exc=True),
        mock_response(200, {"data": "refreshed_data"}),
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
    assert mock_client_session.get.call_count == 3


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
    mock_client_session.get.side_effect = [
        mock_response(200, {"session_token": "expired_session_token"}),
        mock_response(401, {"error": "Unauthorized"}, raise_for_status_exc=True),
        mock_response(200, {}),
    ]

    # First request attempt gets 401
    mock_client_session.request.return_value = mock_response(
        401, {"error": "Unauthorized"}, raise_for_status_exc=True
    )

    async with glpi_session as session:
        with pytest.raises(GLPIUnauthorizedError) as excinfo:
            await session.get("Ticket/123")
        assert "Failed to authenticate after multiple retries" in str(excinfo.value)
        assert excinfo.value.status_code == 401
        assert (
            mock_client_session.request.call_count == 1
        )  # Only one request attempt before giving up

    assert mock_client_session.get.call_count == 3  # init, refresh, killSession


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
        base_url, credentials, refresh_interval=0.2  # type: ignore
    )  # Set a short interval

    # Mock initSession for initial and subsequent proactive refreshes
    mock_client_session.get.side_effect = [
        mock_response(200, {"session_token": "initial_token"}),
        mock_response(200, {"session_token": "proactive_token_1"}),
        mock_response(200, {"session_token": "proactive_token_2"}),
        mock_response(200, {}),
    ]

    async with glpi_session as session:
        assert session._session_token == "initial_token"
        await aio.sleep(0.25)  # Wait for first proactive refresh
        assert session._session_token != "initial_token"
        await aio.sleep(0.25)  # Wait for second proactive refresh
        assert session._session_token == "proactive_token_2"

    # Check that get was called for init + two refreshes + killSession
    assert mock_client_session.get.call_count == 4


@pytest.mark.asyncio
async def test_kill_session_no_token(base_url, app_token, mock_client_session):
    """_kill_session should do nothing if no token is set."""
    creds = Credentials(app_token=app_token, user_token="tok")
    session = GLPISession(base_url, creds)
    session._session = mock_client_session
    session._session_token = None
    await session._kill_session()
    mock_client_session.get.assert_not_called()


@pytest.mark.asyncio
async def test_kill_session_success(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """_kill_session should call the endpoint and clear the token."""
    creds = Credentials(app_token=app_token, user_token=user_token)
    session = GLPISession(base_url, creds)
    session._session = mock_client_session
    session._session_token = user_token
    mock_client_session.get.return_value = mock_response(200, {})
    await session._kill_session()
    mock_client_session.get.assert_called_once_with(
        f"{base_url}/killSession",
        headers={
            "Content-Type": "application/json",
            "Session-Token": user_token,
            "App-Token": app_token,
        },
        proxy=None,
        timeout=ANY,
    )
    assert session._session_token is None


@pytest.mark.asyncio
async def test_request_network_error(
    base_url, app_token, user_token, mock_client_session, mock_response
):
    """Network errors trigger retries and eventually succeed."""

    creds = Credentials(app_token=app_token, user_token=user_token)
    glpi_session = GLPISession(base_url, creds)

    # initSession succeeds
    mock_client_session.get.return_value = mock_response(
        200, {"session_token": user_token}
    )

    err = aiohttp.ClientConnectionError("fail")

    def side_effect(*args, **kwargs):
        if side_effect.calls < 2:
            side_effect.calls += 1
            raise err
        return mock_response(200, {"data": {"id": 1}})

    side_effect.calls = 0
    mock_client_session.request.side_effect = side_effect

    with patch("asyncio.sleep", new=AsyncMock()):
        async with glpi_session as session:
            with pytest.raises(GLPIAPIError):
                await session.get("Ticket/1")

    assert mock_client_session.request.call_count == 1
