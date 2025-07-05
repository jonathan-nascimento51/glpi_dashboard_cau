from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("aiohttp")
import aiohttp

from glpi_dashboard.logging_config import init_logging
from glpi_dashboard.services.exceptions import (
    HTTP_STATUS_ERROR_MAP,
    GLPIAPIError,
    GLPIBadRequestError,
    GLPIForbiddenError,
    GlpiHttpError,
    GLPIInternalServerError,
    GLPINotFoundError,
    GLPITooManyRequestsError,
    GLPIUnauthorizedError,
    glpi_retry,
    parse_error,
)


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
async def test_glpi_retry_success():
    """Tests that the decorator returns the result on the first successful attempt."""

    @glpi_retry(max_retries=3)
    async def mock_api_call():
        return {"status": "success"}

    result = await mock_api_call()
    assert result == {"status": "success"}


@pytest.mark.asyncio
async def test_glpi_retry_on_429_success(mock_response_obj):
    """Tests retry on 429 Too Many Requests with eventual success."""
    call_count = 0

    @glpi_retry(max_retries=3, base_delay=0.01)  # Short delay for testing
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            mock_resp = mock_response_obj(429, "Too Many Requests")
            raise GLPITooManyRequestsError(
                429, parse_error(mock_resp), {"error": "rate limit"}
            )
        return {"status": "success after retry"}

    # Patch asyncio.sleep to avoid actual delays in tests, but still track calls
    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        result = await mock_api_call()
        assert result == {"status": "success after retry"}
        assert call_count == 3
        # Check that sleep was called twice (for 2 retries)
        assert mock_sleep.call_count == 2
        # Verify sleep times are increasing (exponential backoff)
        # Due to jitter, exact values are hard to assert, but order should be preserved
        first_sleep = mock_sleep.call_args_list[0].args[0]
        second_sleep = mock_sleep.call_args_list[1].args[0]
        assert second_sleep >= first_sleep


@pytest.mark.asyncio
async def test_glpi_retry_on_500_success(mock_response_obj):
    """Tests retry on 500 Internal Server Error with eventual success."""
    call_count = 0

    @glpi_retry(max_retries=3, base_delay=0.01)
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            mock_resp = mock_response_obj(500, "Internal Server Error")
            raise GLPIInternalServerError(
                500, parse_error(mock_resp), {"error": "server error"}
            )
        return {"status": "success after 500 retry"}

    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        result = await mock_api_call()
        assert result == {"status": "success after 500 retry"}
        assert call_count == 2
        assert mock_sleep.call_count == 1


@pytest.mark.asyncio
async def test_glpi_retry_max_retries_exceeded():
    """GLPIAPIError is raised if retries exceed the limit for retryable errors."""
    call_count = 0
    max_allowed_retries = 2  # Total attempts = 3 (initial + 2 retries)

    @glpi_retry(max_retries=max_allowed_retries, base_delay=0.01)
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        mock_resp = MagicMock(status=429, reason="Too Many Requests")
        mock_resp.json = AsyncMock(return_value={"error": "rate limit"})
        raise GLPITooManyRequestsError(
            429, parse_error(mock_resp), {"error": "rate limit"}
        )

    with patch("asyncio.sleep", new=AsyncMock()):
        with pytest.raises(GLPITooManyRequestsError) as excinfo:
            await mock_api_call()
        assert excinfo.value.status_code == 429
        assert (
            call_count == max_allowed_retries + 1
        )  # Initial call + max_allowed_retries


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_exception",
    [
        (400, GLPIBadRequestError),
        (401, GLPIUnauthorizedError),
        (403, GLPIForbiddenError),
        (404, GLPINotFoundError),
    ],
)
async def test_glpi_retry_non_retryable_errors(
    status_code, expected_exception, mock_response_obj
):
    """Tests that non-retryable errors are raised immediately and not retried."""
    call_count = 0

    @glpi_retry(max_retries=3, base_delay=0.01)
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        mock_resp = mock_response_obj(status_code, "Test Error")
        error_class = HTTP_STATUS_ERROR_MAP.get(status_code, GLPIAPIError)
        raise error_class(status_code, parse_error(mock_resp), {"error": "test"})

    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        with pytest.raises(expected_exception) as excinfo:
            await mock_api_call()
        assert excinfo.value.status_code == status_code
        assert call_count == 1  # Should not retry
        mock_sleep.assert_not_called()


@pytest.mark.asyncio
async def test_glpi_retry_network_error_success():
    """Tests retry on aiohttp.ClientError (network error) with eventual success."""
    call_count = 0

    @glpi_retry(max_retries=3, base_delay=0.01)
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise aiohttp.ClientConnectionError("Simulated network issue")
        return {"status": "network fixed"}

    with patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:
        result = await mock_api_call()
        assert result == {"status": "network fixed"}
        assert call_count == 2
        assert mock_sleep.call_count == 1


@pytest.mark.asyncio
async def test_glpi_retry_network_error_failure():
    """GLPIAPIError is raised if network errors persist beyond the retry limit."""
    call_count = 0
    max_allowed_retries = 2

    @glpi_retry(max_retries=max_allowed_retries, base_delay=0.01)
    async def mock_api_call():
        nonlocal call_count
        call_count += 1
        raise aiohttp.ClientConnectionError("Simulated persistent network issue")

    with patch("asyncio.sleep", new=AsyncMock()):
        with pytest.raises(GLPIAPIError) as excinfo:
            await mock_api_call()
        assert "Network error after" in str(excinfo.value)
        assert excinfo.value.status_code == 0  # Custom error for network issues
        assert call_count == max_allowed_retries + 1


@pytest.mark.asyncio
async def test_glpi_retry_unexpected_exception():
    """Tests that unexpected exceptions are wrapped in GLPIAPIError."""

    @glpi_retry(max_retries=1)
    async def mock_api_call():
        raise ValueError("Something unexpected happened")

    with pytest.raises(GLPIAPIError) as excinfo:
        await mock_api_call()
    assert "An unexpected error occurred" in str(excinfo.value)
