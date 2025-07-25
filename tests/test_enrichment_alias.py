from unittest.mock import AsyncMock

import pytest

from backend.services.glpi_enrichment import GLPIEnrichmentService


@pytest.mark.asyncio
async def test_enrich_ticket_cache(monkeypatch):
    svc = GLPIEnrichmentService()
    svc._status_map = {2: "OK"}
    svc._user_cache = {7: "Fulano"}
    svc._group_cache = {4: "N2"}
    monkeypatch.setattr(svc, "_fetch_user_name", AsyncMock())
    monkeypatch.setattr(svc, "_fetch_group_name", AsyncMock())
    ticket = {"id": 1, "status": 2, "users_id_recipient": 7, "groups_id_assign": 4}
    result = await svc.enrich_ticket(ticket)
    assert result["user_name"] == "Fulano"
    assert result["group_name"] == "N2"
