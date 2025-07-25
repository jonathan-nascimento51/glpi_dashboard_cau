from unittest.mock import AsyncMock, patch

import pytest

from src.backend.application.glpi_api_client import (
    FORCED_DISPLAY_FIELDS,
    GlpiApiClient,
)
from src.backend.infrastructure.glpi.glpi_session import GLPISession


@pytest.fixture
def mock_glpi_session():
    """Provides a mock GLPISession for dependency injection."""
    session = AsyncMock(spec_set=GLPISession)
    # Mock the return value for session.get to be a tuple (data, headers)
    session.get = AsyncMock(return_value=({}, {}))
    return session


@pytest.mark.asyncio
@patch("src.backend.application.glpi_api_client.paginate_items", new_callable=AsyncMock)
@pytest.mark.parametrize(
    "itemtype, params, expected_endpoint, expected_params_subset",
    [
        (
            "Ticket",
            {"criteria": {"some": "rule"}},
            "search/Ticket",
            {
                "criteria": {"some": "rule"},
                "forcedisplay": FORCED_DISPLAY_FIELDS,
                "expand_dropdowns": 1,
            },
        ),
        (
            "search/Ticket",
            {},
            "Ticket",
            {"forcedisplay": FORCED_DISPLAY_FIELDS, "expand_dropdowns": 1},
        ),
        ("User", {}, "User", {"expand_dropdowns": 1}),
        (
            "User",
            {"criteria": {"is_active": 1}},
            "search/User",
            {"criteria": {"is_active": 1}, "expand_dropdowns": 1},
        ),
    ],
)
async def test_get_all_paginated_builds_correct_request(
    mock_paginate_items,
    mock_glpi_session,
    itemtype,
    params,
    expected_endpoint,
    expected_params_subset,
):
    """
    Verify that get_all_paginated constructs the correct endpoint and parameters
    for various item types and search criteria.
    """
    # Arrange
    client = GlpiApiClient(session=mock_glpi_session)

    # Act
    await client.get_all_paginated(itemtype, **params)

    # Assert: Check that paginate_items was called
    mock_paginate_items.assert_called_once()

    # Extract the dynamically created fetch_page function passed to paginate_items
    fetch_page_func = mock_paginate_items.call_args.args[1]

    # Execute the fetch_page function to trigger the underlying session call
    await fetch_page_func(offset=0, size=100)

    # Assert: Check that the GLPI session was called with the correct arguments
    mock_glpi_session.get.assert_called_once()
    call_args = mock_glpi_session.get.call_args
    actual_endpoint = call_args.args[0]
    actual_params = call_args.kwargs.get("params", {})

    assert actual_endpoint == expected_endpoint
    expected_full_params = {**expected_params_subset, "range": "0-99"}
    assert actual_params == expected_full_params


@pytest.mark.asyncio
async def test_resolve_ticket_fields_success(mock_glpi_session):
    client = GlpiApiClient(session=mock_glpi_session)
    client._mapper.get_search_options = AsyncMock(
        return_value={
            "1": {"field": "id"},
            "2": {"field": "name"},
            "3": {"field": "date_creation"},
            "4": {"field": "priority"},
        }
    )
    await client._resolve_ticket_fields()
    assert client._forced_fields == [1, 2, 3, 4]


@pytest.mark.asyncio
async def test_resolve_ticket_fields_failure(mock_glpi_session):
    client = GlpiApiClient(session=mock_glpi_session)
    client._mapper.get_search_options = AsyncMock(return_value={})
    client._forced_fields = [99]
    await client._resolve_ticket_fields()
    assert client._forced_fields == FORCED_DISPLAY_FIELDS
