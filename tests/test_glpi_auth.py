import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from backend.infrastructure.glpi.glpi_auth import (
    GLPIAuthClient,
    GLPIAuthError,
)


class DummyResponse(requests.Response):
    def __init__(self, status: int, data: Any) -> None:
        super().__init__()
        self.status_code = status
        self._content = json.dumps(data).encode()
        self.headers = requests.structures.CaseInsensitiveDict(
            {"Content-Type": "application/json"}
        )


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


def test_get_session_token_success(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = FakeRedis()
    session = make_session([DummyResponse(200, {"session_token": "tok"})])
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = client.get_session_token()
    assert token == "tok"
    assert redis.get("glpi:session_token") == "tok"
    session.get.assert_called_once()
    session.get.reset_mock()
    assert client.get_session_token() == "tok"
    session.get.assert_not_called()


def test_init_session_unauthorized(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = FakeRedis()
    session = make_session([DummyResponse(401, {})])
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    with pytest.raises(GLPIAuthError):
        client.get_session_token(force_refresh=True)


def test_retry_on_temporary_error(monkeypatch):
    monkeypatch.setenv("DISABLE_RETRY_BACKOFF", "1")
    redis = FakeRedis()
    session = make_session(
        [
            requests.exceptions.ConnectionError("fail"),
            DummyResponse(200, {"session_token": "tok"}),
        ]
    )
    client = GLPIAuthClient(
        base_url="http://example.com/apirest.php",
        app_token="APP",
        user_token="USER",
        redis_conn=redis,
        session=session,
    )
    token = client.get_session_token(force_refresh=True)
    assert token == "tok"
    assert session.get.call_count == 2
