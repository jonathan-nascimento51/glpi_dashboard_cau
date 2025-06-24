import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

import pytest  # noqa: E402
import requests  # noqa: E402
import glpi_api  # noqa: E402


def setup_env():
    os.environ["GLPI_URL"] = "http://example.com"
    os.environ["APP_TOKEN"] = "app"
    os.environ["USER_TOKEN"] = "user"


def test_get_tickets_success(requests_mock):
    setup_env()
    requests_mock.get(
        "http://example.com/initSession",
        json={"session_token": "abc"},
    )
    requests_mock.get(
        "http://example.com/search/Ticket",
        json={"data": [{"id": 1}]},
    )
    tickets = glpi_api.get_tickets(status="new")
    assert isinstance(tickets, list) and len(tickets) == 1


def test_get_tickets_http_error(requests_mock):
    setup_env()
    requests_mock.get(
        "http://example.com/initSession",
        json={"session_token": "abc"},
    )
    requests_mock.get(
        "http://example.com/search/Ticket",
        status_code=500,
    )
    with pytest.raises(requests.HTTPError):
        glpi_api.get_tickets()


def test_login_unauthorized(requests_mock):
    setup_env()
    requests_mock.get("http://example.com/initSession", status_code=401)
    with pytest.raises(glpi_api.UnauthorizedError):
        glpi_api.login()
