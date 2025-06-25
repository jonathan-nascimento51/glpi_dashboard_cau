import os
import pytest
import glpi_api


def setup_env() -> None:
    os.environ["GLPI_URL"] = "http://example.com"
    os.environ["GLPI_APP_TOKEN"] = "app"
    os.environ["GLPI_USER_TOKEN"] = "user"


def test_get_tickets_success(requests_mock) -> None:
    setup_env()
    requests_mock.get(
        "http://example.com/initSession",
        json={"session_token": "t"},
    )
    requests_mock.get(
        "http://example.com/search/Ticket",
        json={"data": [{"id": 1}]},
    )
    tickets = glpi_api.get_tickets()
    assert tickets == [{"id": 1}]


def test_login_unauthorized(requests_mock) -> None:
    setup_env()
    requests_mock.get("http://example.com/initSession", status_code=401)
    with pytest.raises(glpi_api.UnauthorizedError):
        glpi_api.login()
