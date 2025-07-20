from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import aiohttp

from backend.domain.exceptions import (
    GLPIAPIError,
    GlpiHttpError,
    parse_error,
)
from shared.utils.logging import init_logging
from shared.utils.resilience import retry_api_call

pytest.importorskip("aiohttp")


@pytest.fixture(autouse=True)
def _configure_logging() -> None:
    """Ensure logging is configured for tests."""
    init_logging()


@pytest.fixture
def mock_response_obj():
    """Fixture to create a mock aiohttp ClientResponse object."""

    def _mock_response_obj(
        status: int, reason: str = "OK", json_data: Optional[dict] = None
    ):
        mock_resp = MagicMock(spec=aiohttp.ClientResponse)
        mock_resp.status = status
        mock_resp.reason = reason
        mock_resp.json = AsyncMock(
            return_value=json_data if json_data is not None else {}
        )
        mock_resp.text = AsyncMock(
            return_value=str(json_data) if json_data is not None else ""
        )
        mock_resp.request_info = MagicMock()  # Required for ClientResponseError
        mock_resp.history = tuple()  # Required for ClientResponseError
        return mock_resp

    return _mock_response_obj


def test_glpi_http_error_enum():
    """Tests the GlpiHttpError enum values and string representation."""
    assert GlpiHttpError.BAD_REQUEST.value == 400
    assert str(GlpiHttpError.BAD_REQUEST) == "400 Bad Request"
    assert GlpiHttpError.TOO_MANY_REQUESTS.value == 429
    assert str(GlpiHttpError.TOO_MANY_REQUESTS) == "429 Too Many Requests"
    assert GlpiHttpError.INTERNAL_SERVER_ERROR.value == 500
    assert str(GlpiHttpError.INTERNAL_SERVER_ERROR) == "500 Internal Server Error"


def test_parse_error(mock_response_obj):
    """Tests the parse_error function with various response types."""
    # Test with a standard HTTP response
    mock_resp_standard = mock_response_obj(200, "OK")
    msg = parse_error(mock_resp_standard)
    assert msg == "HTTP 200: OK"

    # Test with an error HTTP response
    mock_resp_error = mock_response_obj(400, "Bad Request", {"error": "Invalid input"})
    msg = parse_error(mock_resp_error)
    assert msg == "HTTP 400: Bad Request"

    # Test with a response that has no explicit reason
    mock_resp_no_reason = mock_response_obj(200, None)
    msg = parse_error(mock_resp_no_reason)
    assert msg == "HTTP 200: Unknown Error"

    # Test with unknown status code
    mock_resp_unknown = mock_response_obj(999, "Custom Error")
    msg = parse_error(mock_resp_unknown)
    assert msg == "HTTP 999: Custom Error"


@pytest.mark.asyncio
async def test_retry_api_call_immediate_success():
    """Decorator returns result without retries."""

    @retry_api_call
    async def mock_api_call():
        return {"status": "ok"}

    result = await mock_api_call()
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_retry_api_call_eventual_success():
    """Function succeeds after a few failures."""
    call_count = 0

    @retry_api_call
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise GLPIAPIError(500, "boom")
        return call_count

    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        result = await mock_api_call()
        assert result == 3
        assert call_count == 3
        assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_retry_api_call_max_attempts_exceeded():
    """Original exception is raised after max attempts."""
    call_count = 0

    @retry_api_call
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        raise GLPIAPIError(500, "fail")

    with patch("asyncio.sleep", new=AsyncMock()):
        with pytest.raises(GLPIAPIError):
            await mock_api_call()
        assert call_count == 5
