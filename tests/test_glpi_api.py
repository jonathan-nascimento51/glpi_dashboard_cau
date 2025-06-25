import os
import re

from src.api.glpi_api import GLPIClient


def setup_env() -> None:
    os.environ["GLPI_URL"] = "http://example.com/apirest.php"
    os.environ["GLPI_APP_TOKEN"] = "app"
    os.environ["GLPI_USER_TOKEN"] = "user"


def test_search_returns_items(requests_mock) -> None:
    setup_env()
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "abc"},
    )
    requests_mock.get(
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
        re.compile(r"http://example.com/apirest.php/search/Ticket.*"),
        json={"data": [{"id": 1}]},
        headers={"Content-Range": "0-0/1"},
    )
    client = GLPIClient()
    data = client.search("Ticket")
    assert isinstance(data, list) and len(data) == 1
=======
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
        "http://example.com/search/Ticket",
        json={"data": [{"id": 1}]},
    )
    tickets = glpi_api.get_tickets(status="new")
<<<<<<< ours
    tickets = glpi_api.get_tickets(status="new")
=======
>>>>>>> theirs
    assert isinstance(tickets, list) and len(tickets) == 1
>>>>>>> theirs


def test_retry_on_unauthorized(requests_mock) -> None:
    setup_env()
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "xyz"},
    )
    matcher = re.compile(r"http://example.com/apirest.php/search/Ticket.*")
    requests_mock.get(matcher, status_code=401)
    requests_mock.get(
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
        matcher, json={"data": [{"id": 2}]}, headers={"Content-Range": "0-0/1"}
    )
    client = GLPIClient()
    data = client.search("Ticket")
    assert data[0]["id"] == 2


def test_kill_session(requests_mock) -> None:
    setup_env()
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "zzz"},
    )
    requests_mock.post(
        "http://example.com/apirest.php/killSession",
        status_code=200,
    )
    client = GLPIClient()
    client.kill_session()
    assert client.session_token is None
=======
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
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
<<<<<<< ours
<<<<<<< ours
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
=======
>>>>>>> theirs
