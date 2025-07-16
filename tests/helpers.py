import json
from contextlib import asynccontextmanager
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import aiohttp


class FakeHTTPError(aiohttp.ClientResponseError):
    """Simplified ``ClientResponseError`` used in tests."""

    def __init__(self, status: int, data: Optional[dict] = None) -> None:
        request_info = MagicMock()
        history = ()
        super().__init__(
            request_info=request_info,
            history=history,
            status=status,
            message="HTTP Error",
        )
        self.data = data or {}
        # Some code asserts ``status_code`` like ``requests`` errors
        self.status_code = status


def make_mock_response(
    status: int, json_data: Optional[dict] = None, raise_for_status: bool = False
) -> MagicMock:
    """Create a mock ``aiohttp.ClientResponse`` supporting context manager usage."""
    resp = MagicMock(spec=aiohttp.ClientResponse)
    resp.status = status
    resp.json = AsyncMock(return_value=json_data if json_data is not None else {})
    resp.text = AsyncMock(
        return_value=json.dumps(json_data) if json_data is not None else ""
    )
    resp.request_info = MagicMock()
    resp.history = ()
    if raise_for_status:
        resp.raise_for_status.side_effect = FakeHTTPError(status, json_data)
    else:
        resp.raise_for_status.return_value = None
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


def make_cm(
    status: int, json_data: Optional[dict] = None, raise_for_status: bool = False
):
    """Return an async context manager yielding ``make_mock_response``."""

    @asynccontextmanager
    async def _cm():
        yield make_mock_response(status, json_data, raise_for_status)

    return _cm()
