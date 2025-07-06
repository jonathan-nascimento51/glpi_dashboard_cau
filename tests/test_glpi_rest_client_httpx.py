import re

import pytest
from pytest_httpx import HTTPXMock

from glpi_dashboard.services.exceptions import GLPIAPIError
from glpi_dashboard.services.glpi_rest_client import GLPIClient


@pytest.mark.asyncio
async def test_get_all_paginated_success(httpx_mock: HTTPXMock) -> None:
    """Pagination yields all items across multiple pages."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/search/Ticket\?.*range=0-1.*"),
        json={"data": [{"id": 1}, {"id": 2}]},
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/search/Ticket\?.*range=2-3.*"),
        json={"data": [{"id": 3}]},
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/search/Ticket\?.*range=4-5.*"),
        json={"data": []},
    )

    client = GLPIClient("http://fake-glpi", app_token="app", user_token="tok")
    results = await client.get_all_paginated("Ticket", page_size=2)

    assert len(results) == 3
    assert results[0]["id"] == 1
    assert results[-1]["id"] == 3


@pytest.mark.asyncio
async def test_get_all_paginated_api_error(httpx_mock: HTTPXMock) -> None:
    """The client raises after exhausting retries on server errors."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"http://fake-glpi/search/Ticket.*"),
        status_code=500,
        json={"message": "err"},
        is_reusable=True,
    )

    client = GLPIClient(
        "http://fake-glpi",
        app_token="app",
        user_token="tok",
        retry_max=1,
        retry_base_delay=0.0,
    )

    with pytest.raises(GLPIAPIError):
        await client.get_all_paginated("Ticket", page_size=2)
