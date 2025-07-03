import json
import pytest
import requests

from glpi_dashboard.services.exceptions import GLPIForbiddenError, GLPIInternalServerError, GLPIUnauthorizedError
from glpi_dashboard.services.glpi_api_client import GlpiApiClient
from glpi_dashboard.services.glpi_session import Credentials


class FakeSession:
    def __init__(self, *a, **k):
        self.started = False
        self.killed = False
        self.refreshed = False
        self._session_token = "tok"
        self.verify_ssl = True
        self.proxy = None

    async def __aenter__(self):
        self.started = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.killed = True

    async def _refresh_session_token(self):
        self.refreshed = True
        self._session_token = "newtok"


def patch_session(monkeypatch):
    monkeypatch.setattr(
        "glpi_dashboard.services.glpi_api_client.GLPISession", FakeSession
    )


def test_get_all_pagination(requests_mock, monkeypatch):
    patch_session(monkeypatch)
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        [
            {
                "json": {"data": [{"id": 1, "status": 1}]},
                "headers": {"Content-Range": "0-99/101"},
            },
            {
                "json": {"data": [{"id": 2, "status": 5}]},
                "headers": {"Content-Range": "100-100/101"},
            },
        ],
    )
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        data = client.get_all("Ticket")

    assert [d["status"] for d in data] == ["New", "Solved"]
    history = requests_mock.request_history
    assert history[0].qs["expand_dropdowns"] == ["1"]
    assert history[0].qs["range"] == ["0-99"]
    assert history[1].qs["range"] == ["100-199"]


def test_get_all_refresh_token(requests_mock, monkeypatch):
    patch_session(monkeypatch)
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        [
            {
                "status_code": 401,
                "json": {"message": "ERROR_SESSION_TOKEN_INVALID"},
            },
            {
                "json": {"data": [{"id": 1, "status": 2}]},
                "headers": {"Content-Range": "0-0/1"},
            },
        ],
    )
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        data = client.get_all("Ticket")
        assert client._session.refreshed
    assert data[0]["status"] == "Processing (assigned)"


def test_get_all_http_error(requests_mock, monkeypatch):
    patch_session(monkeypatch)
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        status_code=403,
        json={"message": "Forbidden"},
    )
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        with pytest.raises(GLPIForbiddenError):
            client.get_all("Ticket")


def test_get_all_multiple_pages(requests_mock, monkeypatch):
    patch_session(monkeypatch)
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        [
            {
                "json": {"data": [{"id": 1, "status": 1}]},
                "headers": {"Content-Range": "0-99/250"},
            },
            {
                "json": {"data": [{"id": 2, "status": 2}]},
                "headers": {"Content-Range": "100-199/250"},
            },
            {
                "json": {"data": [{"id": 3, "status": 5}]},
                "headers": {"Content-Range": "200-249/250"},
            },
        ],
    )
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        data = client.get_all("Ticket")

    assert [d["status"] for d in data] == ["New", "Processing (assigned)", "Solved"]
    history = requests_mock.request_history
    assert history[0].qs["range"] == ["0-99"]
    assert history[1].qs["range"] == ["100-199"]
    assert history[2].qs["range"] == ["200-299"]


def test_field_mapping(requests_mock, monkeypatch):
    patch_session(monkeypatch)
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        json={"data": [{"id": 1, "status": 2, "priority": 4, "impact": 3, "type": 1}]},
        headers={"Content-Range": "0-0/1"},
    )
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        data = client.get_all("Ticket")

    item = data[0]
    assert item["status"] == "Processing (assigned)"
    assert item["priority"] == "High"
    assert item["impact"] == "Medium"
    assert item["type"] == "Incident"


def test_search_with_criteria(requests_mock, monkeypatch):
    patch_session(monkeypatch)
    requests_mock.get(
        "http://example.com/apirest.php/search/Ticket",
        json={"data": [{"id": 3, "status": 5}]},
        headers={"Content-Range": "0-0/1"},
    )
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        data = client.search(
            "Ticket",
            [{"field": "status", "searchtype": "equals", "value": 5}],
            forcedisplay=["id", "status"],
        )

    item = data[0]
    assert item["status"] == "Solved"
    q = requests_mock.request_history[0].qs
    assert q["criteria[0][field]"] == ["status"]
    assert q["criteria[0][searchtype]"] == ["equals"]
    assert q["criteria[0][value]"] == ["5"]
    assert q["forcedisplay[0]"] == ["id"]
    assert q["expand_dropdowns"] == ["1"]


def _make_response(status: int, payload: dict | None = None) -> requests.Response:
    """Helper to build a minimal ``requests.Response`` object."""
    resp = requests.Response()
    resp.status_code = status
    resp._content = json.dumps(payload or {}).encode()
    resp.headers = {}
    return resp


def test_request_page_unauthorized(monkeypatch) -> None:
    """401 responses should raise ``GLPIUnauthorizedError``."""

    patch_session(monkeypatch)

    def fake_get(*_a, **_k):
        return _make_response(401, {"message": "unauthorized"})

    monkeypatch.setattr("requests.get", fake_get)

    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        with pytest.raises(GLPIUnauthorizedError):
            client.get_all("Ticket")


def test_request_page_server_error(monkeypatch) -> None:
    """500 responses should raise ``GLPIInternalServerError``."""

    patch_session(monkeypatch)

    def fake_get(*_a, **_k):
        return _make_response(500, {"message": "server error"})

    monkeypatch.setattr("requests.get", fake_get)

    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        with pytest.raises(GLPIInternalServerError):
            client.get_all("Ticket")


def test_flatten_params_invalid(monkeypatch) -> None:
    """Malformed ``params`` should raise an ``AttributeError``."""

    patch_session(monkeypatch)
    creds = Credentials(app_token="app", user_token="u")
    with GlpiApiClient("http://example.com/apirest.php", creds) as client:
        with pytest.raises(AttributeError):
            client._flatten_params(None)  # type: ignore[arg-type]
