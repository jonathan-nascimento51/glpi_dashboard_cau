import logging

import pytest
from fastapi.testclient import TestClient
from shared.utils.logging import SensitiveFilter
from shared.utils.security import validate_glpi_tokens

from worker import create_app


def test_sensitive_filter_masks_token(caplog):
    logger = logging.getLogger("sec")
    handler = logging.StreamHandler()
    handler.addFilter(SensitiveFilter())
    logger.addHandler(handler)
    token = "a" * 40
    with caplog.at_level(logging.INFO):
        logger.info("token: %s", token)
    logger.removeHandler(handler)
    assert "***" in caplog.text


def test_api_token_required(monkeypatch, dummy_cache):
    monkeypatch.setenv("DASHBOARD_API_TOKEN", "secret" * 8)

    async def ok():
        return 200

    monkeypatch.setattr("src.backend.api.worker_api.check_glpi_connection", ok)
    app = create_app(cache=dummy_cache)
    client = TestClient(app)

    resp = client.get("/health")
    assert resp.status_code == 401

    resp = client.get("/health", headers={"X-API-Token": "secret" * 8})
    assert resp.status_code == 200


def test_validate_tokens_fails(monkeypatch):
    monkeypatch.setenv("GLPI_APP_TOKEN", "")
    monkeypatch.setenv("GLPI_USER_TOKEN", "")
    with pytest.raises(SystemExit):
        validate_glpi_tokens()
