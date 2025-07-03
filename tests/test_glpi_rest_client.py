import httpx
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from glpi_dashboard.services.glpi_rest_client import GLPIClient  # noqa: E402


@pytest.mark.asyncio
async def test_list_search_options(monkeypatch):
    client = GLPIClient(
        "http://example.com/apirest.php", app_token="app", user_token="tok"
    )

    async def fake_get(url, params=None):
        assert url == "listSearchOptions/Ticket"
        return httpx.Response(200, json={"1": {"name": "ID", "datatype": "int"}})

    monkeypatch.setattr(client._client, "get", fake_get)

    data = await client.list_search_options("Ticket")
    assert data["1"]["name"] == "ID"
