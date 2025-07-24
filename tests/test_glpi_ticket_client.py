import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from glpi_ticket_client import GLPITicketClient


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


class FakeAuth:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.calls = 0

    def get_session_token(self, force_refresh: bool = False):
        self.calls += 1
        return self.tokens.pop(0)


def test_list_tickets_basic(monkeypatch):
    resp = DummyResponse(200, {"data": [{"id": 1}]})
    session = make_session([resp])
    client = GLPITicketClient(
        base_url="http://example.com/apirest.php",
        auth_client=FakeAuth(["tok"]),
        session=session,
    )

    tickets = client.list_tickets(filters={"status": "new"}, page=1, page_size=50)

    assert tickets == [{"id": 1}]
    args, kwargs = session.get.call_args
    assert args[0] == "http://example.com/apirest.php/search/Ticket"
    assert kwargs["headers"]["Session-Token"] == "tok"
    assert kwargs["params"]["criteria[0][field]"] == "status"
    assert kwargs["params"]["range"] == "0-49"


def test_pagination(monkeypatch):
    session = make_session([DummyResponse(200, {"data": []})])
    client = GLPITicketClient(
        base_url="http://ex.com/api", auth_client=FakeAuth(["a"]), session=session
    )
    client.list_tickets(page=2, page_size=10)
    params = session.get.call_args.kwargs["params"]
    assert params["range"] == "10-19"


def test_retry_on_401(monkeypatch):
    responses = [DummyResponse(401, {}), DummyResponse(200, {"data": [{"id": 2}]})]
    session = make_session(responses)
    auth = FakeAuth(["old", "new"])
    client = GLPITicketClient(
        base_url="http://ex.com/api", auth_client=auth, session=session
    )

    tickets = client.list_tickets()

    assert tickets == [{"id": 2}]
    assert auth.calls == 2
    assert session.get.call_count == 2


def test_http_error(monkeypatch):
    session = make_session([DummyResponse(403, {"error": "forbidden"})])
    client = GLPITicketClient(
        base_url="http://ex.com/api", auth_client=FakeAuth(["tok"]), session=session
    )
    with pytest.raises(requests.HTTPError):
        client.list_tickets()
