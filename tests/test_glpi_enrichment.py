from unittest.mock import AsyncMock

import pytest

from backend.services.glpi_enrichment import GLPIEnrichmentService


@pytest.mark.asyncio
async def test_enrich_ticket_cache_hit(mocker):
    svc = GLPIEnrichmentService()
    svc._status_map = {2: "Em andamento"}
    svc._user_cache = {7: "Fulano"}
    svc._group_cache = {4: "N2"}
    mocker.patch.object(
        svc,
        "_fetch_user_name",
        side_effect=AssertionError("fetch_user_name should not be called"),
    )
    mocker.patch.object(
        svc,
        "_fetch_group_name",
        side_effect=AssertionError("fetch_group_name should not be called"),
    )

    ticket = {"id": 1, "status": 2, "users_id_recipient": 7, "groups_id_assign": 4}
    result = await svc.enrich_ticket(ticket)

    assert result["status_name"] == "Em andamento"
    assert result["user_name"] == "Fulano"
    assert result["group_name"] == "N2"


@pytest.mark.asyncio
async def test_enrich_ticket_missing_user(mocker):
    svc = GLPIEnrichmentService()
    svc._status_map = {2: "Em andamento"}
    fetch = mocker.patch.object(
        svc, "_fetch_user_name", new=AsyncMock(return_value="Fulano")
    )

    ticket = {"id": 1, "status": 2, "users_id_recipient": 9}
    result = await svc.enrich_ticket(ticket)

    assert result["user_name"] == "Fulano"
    assert svc._user_cache[9] == "Fulano"
    fetch.assert_awaited_once_with(9)


@pytest.mark.asyncio
async def test_enrich_tickets_deduplicates_calls(mocker):
    svc = GLPIEnrichmentService()
    svc._status_map = {2: "OK"}
    fetch_user = mocker.patch.object(
        svc, "_fetch_user_name", new=AsyncMock(return_value="User")
    )
    fetch_group = mocker.patch.object(
        svc, "_fetch_group_name", new=AsyncMock(return_value="Group")
    )

    tickets = [
        {"id": 1, "users_id_recipient": 5, "groups_id_assign": 2},
        {"id": 2, "users_id_recipient": 5, "groups_id_assign": 2},
    ]
    result = await svc.enrich_tickets(tickets)

    assert all(t["user_name"] == "User" for t in result)
    assert all(t["group_name"] == "Group" for t in result)
    fetch_user.assert_awaited_once_with(5)
    fetch_group.assert_awaited_once_with(2)


@pytest.mark.asyncio
async def test_skip_when_already_expanded(mocker):
    svc = GLPIEnrichmentService()
    get_status = mocker.patch.object(
        svc, "_get_status_name", side_effect=AssertionError("should not be called")
    )

    ticket = {"id": 1, "status": 2, "status_name": "Existing"}
    result = await svc.enrich_ticket(ticket)

    assert result["status_name"] == "Existing"
    get_status.assert_not_called()
