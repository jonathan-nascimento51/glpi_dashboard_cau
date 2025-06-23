import os
import sys
import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import glpi_api


def setup_env():
    os.environ["GLPI_URL"] = "http://example.com"
    os.environ["APP_TOKEN"] = "app"
    os.environ["USER_TOKEN"] = "user"


def test_get_tickets_success(requests_mock):
    setup_env()
    requests_mock.get("http://example.com/initSession", json={"session_token": "abc"})
    requests_mock.get("http://example.com/tickets", json=[{"id": 1}])
    tickets = glpi_api.get_tickets()
    assert isinstance(tickets, list) and len(tickets) == 1


def test_get_tickets_http_error(requests_mock):
    setup_env()
    requests_mock.get("http://example.com/initSession", json={"session_token": "abc"})
    requests_mock.get("http://example.com/tickets", status_code=500)
    with pytest.raises(requests.HTTPError):
        glpi_api.get_tickets()