import os
import re

from src.api.glpi_api import GLPIClient
from src.etl.tickets_groups import collect_tickets_with_groups


def setup_env() -> None:
    os.environ["GLPI_URL"] = "http://example.com/apirest.php"
    os.environ["GLPI_APP_TOKEN"] = "app"
    os.environ["GLPI_USER_TOKEN"] = "user"


def mock_common(requests_mock):
    requests_mock.post(
        "http://example.com/apirest.php/initSession",
        json={"session_token": "t"},
    )


def test_collect_basic(requests_mock):
    setup_env()
    mock_common(requests_mock)
    requests_mock.get(
        re.compile(r"http://example.com/apirest.php/search/Ticket.*"),
        json={
            "data": [{"id": 1, "name": "t", "status": 1, "date": "2024-01-01"}]
        },
        headers={"Content-Range": "0-0/1"},
    )
    requests_mock.get(
        re.compile(r"http://example.com/apirest.php/search/Ticket_User.*"),
        json={"data": [{"users_id": 2, "groups_id": 3}]},
        headers={"Content-Range": "0-0/1"},
    )
    requests_mock.get(
        "http://example.com/apirest.php/User/2",
        json={"id": 2, "name": "Alice", "groups_id": 3},
    )
    requests_mock.get(
        "http://example.com/apirest.php/Group/3",
        json={"id": 3, "completename": "N1"},
    )
    client = GLPIClient()
    df = collect_tickets_with_groups("2024-01-01", "2024-01-02", client=client)
    assert len(df) == 1
    assert df.iloc[0]["group_name"] == "N1"
