import os
import pytest
from src.api.glpi_api import GLPIClient
import json


def setup_env() -> None:
    os.environ["GLPI_URL"] = "http://example.com"
    os.environ["GLPI_APP_TOKEN"] = "app"
    os.environ["GLPI_USER_TOKEN"] = "user"


def test_search_success(requests_mock) -> None:
    setup_env()
    requests_mock.post(
        "http://example.com/initSession",
        json={"session_token": "t"},
    )
    requests_mock.get(
        "http://example.com/search/Ticket",
        json={"data": [{"id": 1}]},
        headers={"Content-Range": "0-0/1"},
    )
    client = GLPIClient()
    data = client.search("Ticket")
    assert data == [{"id": 1}]


def test_start_session_unauthorized(requests_mock) -> None:
    setup_env()
    requests_mock.post("http://example.com/initSession", status_code=401)
    client = GLPIClient()
    with pytest.raises(Exception):
        client.start_session()


def test_kill_session(requests_mock) -> None:
    """Starting and killing a session clears the stored token."""
    setup_env()
    requests_mock.post(
        "http://example.com/initSession",
        json={"session_token": "tok"},
    )
    requests_mock.post(
        "http://example.com/killSession",
        status_code=200,
    )
    client = GLPIClient()
    client.start_session()
    assert client.session_token == "tok"
    client.kill_session()
    assert client.session_token is None
    assert "Session-Token" not in client.session.headers
