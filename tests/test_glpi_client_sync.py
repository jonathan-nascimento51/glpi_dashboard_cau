from types import SimpleNamespace
from typing import Any
from unittest.mock import ANY, MagicMock

import pytest
import requests

from backend.infrastructure.glpi.glpi_client import (
    GLPIClientNotFound,
    GLPISessionManager,
    SearchCriteriaBuilder,
    get_secret,
)


class DummyResponse(requests.Response):
    def __init__(self, status: int, json_data: Any) -> None:
        super().__init__()
        self.status_code = status
        import json

        self._content = json.dumps(json_data).encode()
        self.headers = requests.structures.CaseInsensitiveDict(
            {"Content-Type": "application/json"}
        )


def make_session(responses):
    def side(lst):
        calls = list(lst)

        def _inner(*args, **kwargs):
            return calls.pop(0) if calls else lst[-1]

        return _inner

    session = SimpleNamespace()
    session.get = MagicMock(side_effect=side(responses.get("get", [])))
    session.request = MagicMock(side_effect=side(responses.get("request", [])))
    session.close = MagicMock()
    return session


def test_get_secret_env(monkeypatch):
    monkeypatch.setenv("TOKEN", "abc")
    assert get_secret("TOKEN") == "abc"


def test_get_secret_missing(monkeypatch):
    monkeypatch.delenv("TOKEN", raising=False)
    monkeypatch.delenv("TOKEN_FILE", raising=False)
    with pytest.raises(RuntimeError):
        get_secret("TOKEN")


def test_get_secret_file(monkeypatch, tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("xyz")
    monkeypatch.setenv("TOKEN_FILE", str(f))
    assert get_secret("TOKEN") == "xyz"


def test_session_manager_basic(monkeypatch):
    init_resp = DummyResponse(200, {"session_token": "tok"})
    kill_resp = DummyResponse(200, {})
    req_resp = DummyResponse(200, {"id": 1})
    session = make_session({"get": [init_resp, kill_resp], "request": [req_resp]})
    mgr = GLPISessionManager(
        "http://example.com/apirest.php",
        "APP",
        user_token="USER",
        session=session,
    )
    with mgr as m:
        data = m.get_item("Ticket", 1)
        assert data == {"id": 1}
    assert session.get.call_count == 2  # init and kill
    session.request.assert_called_with(
        "GET",
        "http://example.com/apirest.php/Ticket/1",
        headers=ANY,
        verify=True,
    )


def test_error_mapping(monkeypatch):
    init_resp = DummyResponse(200, {"session_token": "tok"})
    err_resp = DummyResponse(404, {"error": "no"})
    session = make_session(
        {"get": [init_resp, DummyResponse(200, {})], "request": [err_resp]}
    )
    mgr = GLPISessionManager(
        "http://example.com/apirest.php",
        "APP",
        user_token="USER",
        session=session,
    )
    with mgr:
        with pytest.raises(GLPIClientNotFound):
            mgr.get_item("Ticket", 2)


def test_search_builder_params():
    builder = SearchCriteriaBuilder().add("1", "a").between("2", "x", "y")
    params = builder.build()
    assert params["criteria[0][field]"] == "1"
    assert params["criteria[1][searchtype]"] == "between"


def test_search_by_date_range(monkeypatch):
    init_resp = DummyResponse(200, {"session_token": "tok"})
    kill_resp = DummyResponse(200, {})
    req_resp = DummyResponse(200, [])
    session = make_session({"get": [init_resp, kill_resp], "request": [req_resp]})
    mgr = GLPISessionManager(
        "http://example.com/apirest.php",
        "APP",
        user_token="USER",
        session=session,
    )
    with mgr:
        mgr.search_by_date_range("Ticket", "date", "2024-01-01", "2024-01-31")
    args, kwargs = session.request.call_args
    assert args[0] == "GET" and args[1].endswith("search/Ticket")
    assert "criteria[0][field]" in kwargs["params"]
    assert kwargs["headers"]["Session-Token"] == "tok"
