import os

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
