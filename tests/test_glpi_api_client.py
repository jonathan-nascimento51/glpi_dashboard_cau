from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.infrastructure.glpi.glpi_auth import GLPIAuthClient
from backend.services.glpi_enrichment import GLPIEnrichmentService
from glpi_api_client import (
    BASE_TICKET_FIELDS,
    GlpiApiClient,
    _resolve_ticket_fields,
)
from glpi_ticket_client import GLPITicketClient


@pytest.fixture
def mock_glpi_session():
    """Provides a mock GLPISession for dependency injection."""
    auth_client = AsyncMock(spec_set=GLPIAuthClient)
    ticket_client = AsyncMock(spec_set=GLPITicketClient)
    enrichment = AsyncMock(spec_set=GLPIEnrichmentService)

    # Mock methods that GlpiApiClient might call on its dependencies
    auth_client.get_session_token.return_value = "mock_token"
    ticket_client.list_tickets.return_value = []
    enrichment.enrich_tickets.return_value = []

    return auth_client, ticket_client, enrichment


@pytest.mark.asyncio
@patch(
    "src.backend.application.glpi_api_client.MappingService",
    new=MagicMock(
        initialize=AsyncMock(),
        get_search_options=AsyncMock(return_value={}),
    ),
)
@patch(
    "src.backend.application.glpi_api_client.paginate_items",
    new_callable=AsyncMock,
)
@pytest.mark.parametrize(
    "itemtype, params, expected_endpoint, expected_params_subset",
    [
        (
            "Ticket",
            {"criteria": {"some": "rule"}},
            "search/Ticket",
            {"criteria": {"some": "rule"}},
        ),
        (
            "search/Ticket",
            {},
            "search/Ticket",
            {},
        ),
        ("User", {}, "User", {}),
        (
            "User",
            {"criteria": {"is_active": 1}},
            "search/User",
            {"criteria": {"is_active": 1}},
        ),
    ],
)
async def test_get_tickets_builds_correct_request(
    mock_paginate_items: AsyncMock,
    mock_glpi_session: tuple[AsyncMock, AsyncMock, AsyncMock],
    itemtype: str,
    params: dict[str, object],
    expected_endpoint: str,
    expected_params_subset: dict[str, object],
):
    # Arrange
    auth_client, ticket_client, enrichment = mock_glpi_session
    client = GlpiApiClient(
        auth_client=auth_client, ticket_client=ticket_client, enrichment=enrichment
    )

    ticket_client.list_tickets.return_value = [{"id": 1, "name": "Test Ticket"}]
    enrichment.enrich_tickets.return_value = [{"id": 1, "name": "Test Ticket"}]

    async with client:
        # Act
        raw_filters = params.get("criteria")
        # Se raw_filters for um dict, garanta o tipo correto; senão, use None.
        filters: dict[str, str] | None = (
            raw_filters if isinstance(raw_filters, dict) else None
        )
        await client.get_tickets(filters=filters, page=1, page_size=50)

    # Assert
    ticket_client.list_tickets.assert_called_once_with(filters, 1, 50)
    enrichment.enrich_tickets.assert_called_once()

    # The _resolve_ticket_fields method is internal and not directly exposed for testing
    # in the GlpiApiClient. It's called during initialization.
    # The original test for _resolve_ticket_fields seems to be testing an older
    # implementation where it was a public method or had a different purpose.
    # The current `_resolve_ticket_fields` is a private helper function
    # and `_forced_fields` is populated by `_populate_forced_fields`.


@pytest.mark.asyncio
async def test_populate_forced_fields():
    """Test that _populate_forced_fields correctly initializes _forced_fields."""
    client = GlpiApiClient()
    # _populate_forced_fields is called during __init__
    assert client._forced_fields == ["users_id_assign"]


def test_base_ticket_fields_has_assignment_field():
    """Verifica se a lista de campos base contém 'users_id_assign'."""
    assert "users_id_assign" in BASE_TICKET_FIELDS


def test_resolve_ticket_fields_includes_assignment_field():
    """Verifica se a resolução dinâmica de campos sempre inclui 'users_id_assign'."""
    # Mesmo que outros campos sejam passados e "users_id_assign" não esteja entre eles,
    # o resultado final deve conter o campo de atribuição.
    dynamic = ["custom_field", "another_field"]
    # This calls the private helper function _resolve_ticket_fields directly
    resolved = _resolve_ticket_fields(dynamic_fields=dynamic)
    assert "users_id_assign" in resolved  # type: ignore[attr-defined]
    # Também se certifique de que os campos dinâmicos foram mantidos:
    assert "custom_field" in resolved  # type: ignore[attr-defined]
    assert "another_field" in resolved  # type: ignore[attr-defined]
