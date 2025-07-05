from unittest.mock import AsyncMock, patch

import httpx
import pytest

from glpi_dashboard.glpi_client import GLPIApiClient


@pytest.mark.asyncio
async def test_request_retry_on_503(httpx_mock):
    httpx_mock.add_response(status_code=503)
    httpx_mock.add_response(status_code=503)
    httpx_mock.add_response(status_code=200, json={"ok": True})

    client = GLPIApiClient("http://example.com/api", httpx.AsyncClient())
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        resp = await client._request("GET", "ping")

    assert resp.status_code == 200
    assert sleep_mock.call_count == 2
    assert len(httpx_mock.get_requests()) == 3


@pytest.mark.asyncio
async def test_request_retry_on_timeout(httpx_mock):
    httpx_mock.add_exception(httpx.ReadTimeout("boom"))
    httpx_mock.add_response(status_code=200, json={"ok": True})

    client = GLPIApiClient("http://example.com/api", httpx.AsyncClient())
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        resp = await client._request("GET", "ping")

    assert resp.status_code == 200
    assert sleep_mock.call_count == 1
    assert len(httpx_mock.get_requests()) == 2
