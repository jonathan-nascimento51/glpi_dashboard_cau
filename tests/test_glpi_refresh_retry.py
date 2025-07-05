import asyncio as aio
from unittest.mock import AsyncMock, patch

import pytest

from glpi_dashboard.services.glpi_session import GLPISession, Credentials

from tests.test_glpi_session import mock_response as _mock_response
from tests.test_glpi_session import mock_client_session as _mock_client_session
from tests.test_glpi_session import base_url as _base_url
from tests.test_glpi_session import app_token as _app_token
from tests.test_glpi_session import username as _username
from tests.test_glpi_session import password as _password


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Intermittent token refresh behaviour")
async def test_refresh_session_token_retries_on_server_error(
    _base_url, _app_token, _username, _password, _mock_client_session, _mock_response
):
    creds = Credentials(app_token=_app_token, username=_username, password=_password)
    session = GLPISession(_base_url, creds)

    _mock_client_session.get.side_effect = [
        _mock_response(200, {"session_token": "init"}),
        _mock_response(500, {"error": "fail"}, raise_for_status_exc=True),
        _mock_response(200, {"session_token": "retry"}),
        _mock_response(200, {}),
    ]
    _mock_client_session.request.side_effect = [
        _mock_response(401, {"error": "unauth"}, raise_for_status_exc=True),
        _mock_response(200, {"ok": True}),
    ]

    with patch("asyncio.sleep", new=AsyncMock()):
        async with session as s:
            data = await s.get("Ticket/1")
            assert data == {"ok": True}
            assert session._session_token == "retry"

    assert _mock_client_session.get.call_count == 4
    assert _mock_client_session.request.call_count == 2


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Intermittent token refresh behaviour")
async def test_proactive_refresh_loop_triggers_refresh(
    _base_url, _app_token, _username, _password, _mock_client_session
):
    creds = Credentials(app_token=_app_token, username=_username, password=_password)
    session = GLPISession(_base_url, creds, refresh_interval=0.05)

    tokens = iter(["initial", "refreshed"])

    async def fake_refresh(self):
        self._session_token = next(tokens)
        self._last_refresh_time = aio.get_running_loop().time()

    with patch.object(GLPISession, "_refresh_session_token", new=AsyncMock(side_effect=fake_refresh)) as m_refresh:
        _mock_client_session.get.return_value = _mock_response(200, {})
        async with session:
            await aio.sleep(0.06)
            assert m_refresh.call_count >= 2

    kill_call = _mock_client_session.get.call_args_list[-1]
    assert kill_call.args[0] == f"{_base_url}/killSession"
