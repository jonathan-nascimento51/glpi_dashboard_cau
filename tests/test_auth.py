from types import SimpleNamespace
from unittest.mock import MagicMock

import fakeredis
import pytest
from backend.infrastructure.glpi.glpi_auth import GLPIAuthClient, GLPIAuthError

from tests.helpers import make_cm

pytest.importorskip("aiohttp")  # noqa: E402


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


@pytest.mark.asyncio
async def test_init_session_success(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = fakeredis.FakeRedis(decode_responses=True)
    session = make_session([make_cm(200, {"session_token": "tok"})])
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = await client.init_session()
    assert token == "tok"
    assert await redis.get("glpi:session_token") is None


@pytest.mark.asyncio
async def test_init_session_failure(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = fakeredis.FakeRedis(decode_responses=True)
    session = make_session([make_cm(401, {})])
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
async def test_get_session_token_cache(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = fakeredis.FakeRedis(decode_responses=True)
    await redis.set("glpi:session_token", "cached")
    session = make_session([])
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = await client.get_session_token()
    assert token == "cached"
    session.get.assert_not_called()
