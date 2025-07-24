from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from glpi_http_utils import GLPIPermissionError
from glpi_ticket_client import GLPITicketClient


class DummyResponse:
    def __init__(self, status, data):
        self.status_code = status
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise GLPIPermissionError()


def make_session(responses):
    def side_effect(*args, **kwargs):
        result = responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    session = SimpleNamespace()
    session.request = MagicMock(side_effect=side_effect)
    session.get = session.request
    return session


class FakeAuth:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.calls = 0

    def get_session_token(self, force_refresh=False):
        self.calls += 1
        return self.tokens.pop(0)


def test_list_tickets_basic():
    resp = DummyResponse(200, {"data": [{"id": 1}]})
    session = make_session([resp])
    client = GLPITicketClient(
        base_url="http://example.com/apirest.php",
        auth_client=FakeAuth(["tok"]),
        session=session,
    )
    result = client.list_tickets({"status": "new"}, page=1, page_size=50)
    assert result == [{"id": 1}]
    assert session.request.call_args.args[0] == "GET"


def test_retry_on_401():
    responses = [DummyResponse(401, {}), DummyResponse(200, {"data": [{"id": 2}]})]
    session = make_session(responses)
    auth = FakeAuth(["old", "new"])
    client = GLPITicketClient(
        base_url="http://example.com", auth_client=auth, session=session
    )
    result = client.list_tickets()
    assert result == [{"id": 2}]
    assert auth.calls == 2


def test_http_error():
    session = make_session([DummyResponse(403, {})])
    client = GLPITicketClient(
        base_url="http://example.com", auth_client=FakeAuth(["tok"]), session=session
    )
    with pytest.raises(GLPIPermissionError):
        client.list_tickets()
