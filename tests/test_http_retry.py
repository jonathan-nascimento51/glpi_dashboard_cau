import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import requests

from glpi_http_utils import (
    GLPIPermissionError,
    GLPIRetryError,
    http_request_with_retry,
)


class DummyResponse(requests.Response):
    def __init__(self, status: int, data: dict | None = None) -> None:
        super().__init__()
        self.status_code = status
        self._content = json.dumps(data or {}).encode()
        self.headers = requests.structures.CaseInsensitiveDict(
            {"Content-Type": "application/json"}
        )
        self.request = MagicMock(url="http://example.com")


def make_session(responses):
    def side_effect(*args, **kwargs):
        result = responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    session = SimpleNamespace()
    session.request = MagicMock(side_effect=side_effect)
    return session


class FakeAuth:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.calls = 0

    def get_session_token(self, force_refresh: bool = False):
        self.calls += 1
        return self.tokens.pop(0)


def test_retry_on_5xx_eventual_success():
    session = make_session(
        [
            DummyResponse(502, {}),
            DummyResponse(502, {}),
            DummyResponse(200, {"ok": True}),
        ]
    )
    auth = FakeAuth(["a"])
    with patch("time.sleep") as sleep:
        resp = http_request_with_retry(
            session,
            "GET",
            "http://example.com",
            headers={},
            auth_client=auth,
            max_attempts=4,
        )
    assert resp.status_code == 200
    assert session.request.call_count == 3
    assert sleep.call_count == 2


def test_refresh_on_401():
    session = make_session([DummyResponse(401, {}), DummyResponse(200, {"ok": True})])
    auth = FakeAuth(["old", "new"])
    with patch("time.sleep") as sleep:
        resp = http_request_with_retry(
            session,
            "GET",
            "http://example.com",
            headers={"Session-Token": "old"},
            auth_client=auth,
            max_attempts=2,
        )
    assert resp.status_code == 200
    assert auth.calls == 1
    assert session.request.call_count == 2
    sleep.assert_not_called()


def test_permission_error():
    session = make_session([DummyResponse(403, {})])
    with pytest.raises(GLPIPermissionError):
        http_request_with_retry(
            session,
            "GET",
            "http://example.com",
            headers={},
            auth_client=FakeAuth(["tok"]),
        )
    assert session.request.call_count == 1


def test_retry_error_after_max_attempts():
    session = make_session([requests.ConnectionError("boom")] * 3)
    with patch("time.sleep"):
        with pytest.raises(GLPIRetryError):
            http_request_with_retry(
                session,
                "GET",
                "http://example.com",
                headers={},
                auth_client=FakeAuth(["tok"]),
                max_attempts=3,
            )
    assert session.request.call_count == 3
