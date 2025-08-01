from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest import MonkeyPatch

from backend.infrastructure.glpi.glpi_auth import GLPIAuthClient, GLPIAuthError


def make_cm(status: int, json_data: dict):
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=json_data)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=mock_resp)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm


@pytest.mark.asyncio
async def test_init_session_success(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis: Any = MagicMock()
    redis.get = AsyncMock(return_value=None)
    session: Any = MagicMock()
    session.get = MagicMock(
        side_effect=lambda *a, **kw: make_cm(200, {"session_token": "tok"})
    )
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = await client.init_session()
    assert token == "tok"


@pytest.mark.asyncio
async def test_init_session_failure(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis: Any = MagicMock()
    session: Any = MagicMock()
    # Corrija para mockar corretamente o async context manager
    session.get = MagicMock(side_effect=lambda *a, **kw: make_cm(401, {}))
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    with pytest.raises(GLPIAuthError):
        await client.init_session()


@pytest.mark.asyncio
async def test_get_session_token_cache(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis: Any = MagicMock()
    redis.get = AsyncMock(return_value="cached")
    session: Any = MagicMock()
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = await client.get_session_token()
    assert token == "cached"
    assert not session.get.called
