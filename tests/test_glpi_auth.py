from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pytest.importorskip("aiohttp")

import aiohttp  # noqa: E402
from backend.infrastructure.glpi.glpi_auth import (  # noqa: E402
    GLPIAuthClient,
    GLPIAuthError,
)

from tests.helpers import make_cm  # noqa: E402


def make_session(responses):
    def side(lst):
        calls = list(lst)

        def _inner(*args, **kwargs):
            result = calls.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        return _inner

    session = SimpleNamespace()
    session.get = MagicMock(side_effect=side(responses))
    return session


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def get(self, key: str):
        return self.store.get(key)

    def setex(self, key: str, ttl: int, value: str):
        self.store[key] = value


@pytest.mark.asyncio
async def test_get_session_token_success(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = FakeRedis()
    session = make_session([make_cm(200, {"session_token": "tok"})])
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = await client.get_session_token()
    assert token == "tok"
    assert redis.get("glpi:session_token") == "tok"
    session.get.assert_called_once()
    session.get.reset_mock()
    assert await client.get_session_token() == "tok"
    session.get.assert_not_called()


@pytest.mark.asyncio
async def test_init_session_unauthorized(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = FakeRedis()
    session = make_session([make_cm(401, {})])
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    with pytest.raises(GLPIAuthError):
        await client.get_session_token(force_refresh=True)


@pytest.mark.asyncio
async def test_retry_on_temporary_error(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = FakeRedis()
    session = make_session(
        [
            aiohttp.ClientConnectionError("fail"),
            make_cm(200, {"session_token": "tok"}),
        ]
    )
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = await client.get_session_token(force_refresh=True)
    assert token == "tok"
    assert session.get.call_count == 2
