import os
import json

from src.api.glpi_api import GLPIClient


def setup_env():
    os.environ["GLPI_URL"] = "http://example.com/apirest.php"
    os.environ["GLPI_APP_TOKEN"] = "app"
    os.environ["GLPI_USER_TOKEN"] = "user"


def test_search_pagination(requests_mock):
    setup_env()
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "abc"},
    )
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        json={"data": [{"id": 1}]},
        headers={"Content-Range": "0-0/1"},
    )
    client = GLPIClient()
    data = client.search("Ticket")
    assert data == [{"id": 1}]


def test_kill_session(requests_mock):
    """Verify that kill_session clears token and header."""
    setup_env()
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "abc"},
    )
    requests_mock.post(
        "http://example.com/apirest.php/killSession",
        status_code=200,
    )
    client = GLPIClient()
    client.start_session()
    assert client.session_token == "abc"
    client.kill_session()
    assert client.session_token is None
    assert "Session-Token" not in client.session.headers
