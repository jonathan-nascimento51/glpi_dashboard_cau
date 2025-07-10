import asyncio as aio
from unittest.mock import AsyncMock, patch

import pytest

from backend.adapters.glpi_session import Credentials, GLPISession


@pytest.mark.asyncio
async def test_refresh_session_token_retries_on_server_error(
    base_url,
    app_token,
    username,
    password,
    mock_client_session,
    mock_response,
):
    creds = Credentials(app_token=app_token, username=username, password=password)
    session = GLPISession(base_url, creds)

    mock_client_session.side_effect = [
        mock_response(200, {"session_token": "init"}),
        mock_response(500, {"error": "fail"}, raise_for_status_exc=True),
        mock_response(200, {"session_token": "retry"}),
        mock_response(200, {}),
    ]
    mock_client_session.request.side_effect = [
        mock_response(401, {"error": "unauth"}, raise_for_status_exc=True),
        mock_response(200, {"ok": True}),
    ]

    with patch("asyncio.sleep", new=AsyncMock()):
        async with session as s:
            data = await s.get("Ticket/1")
            assert data == {"ok": True}
            assert session._session_token == "retry"

    assert mock_client_session.call_count == 4
    assert mock_client_session.request.call_count == 2


@pytest.mark.asyncio
async def test_proactive_refresh_loop_triggers_refresh(
    base_url,
    app_token,
    username,
    password,
    mock_client_session,
    mock_response,
):
    creds = Credentials(app_token=app_token, username=username, password=password)
    session = GLPISession(base_url, creds, refresh_interval=5)

    tokens = iter(["initial", "refreshed"])

    async def fake_refresh(self):
        self._session_token = next(tokens)
        self._last_refresh_time = aio.get_running_loop().time()

    with patch.object(
        GLPISession, "_refresh_session_token", new=AsyncMock(side_effect=fake_refresh)
    ) as m_refresh:
        mock_client_session.return_value = mock_response(200, {})
        async with session:
            await aio.sleep(0.06)
            assert m_refresh.call_count >= 2

    kill_call = mock_client_session.call_args_list[-1]
    assert kill_call.args[0] == f"{base_url}/killSession"
