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

    app = create_app(cache=dummy_cache)
    client = TestClient(app)

    resp = client.get("/health")
    assert resp.status_code == 401

    resp = client.get("/health", headers={"X-API-Token": "secret" * 8})
    assert resp.status_code == 200


def test_validate_tokens_fails_on_missing(monkeypatch):
    monkeypatch.setenv("GLPI_APP_TOKEN", "")
    monkeypatch.setenv("GLPI_USER_TOKEN", "")
    with pytest.raises(SystemExit):
        validate_glpi_tokens()


@pytest.mark.parametrize(
    "app_token, user_token",
    [
        ("a" * 40, "short"),  # user_token too short
        ("not-hex-string", "b" * 40),  # app_token not hex
        ("a" * 40, "b" * 39),  # user_token too short
    ],
)
def test_validate_tokens_fails_on_invalid_format(
    monkeypatch, caplog, app_token, user_token
):
    monkeypatch.setenv("GLPI_APP_TOKEN", app_token)
    monkeypatch.setenv("GLPI_USER_TOKEN", user_token)
    with pytest.raises(SystemExit), caplog.at_level(logging.CRITICAL):
        validate_glpi_tokens()

    assert "GLPI token format appears invalid" in caplog.text


def test_validate_tokens_success(monkeypatch):
    monkeypatch.setenv("GLPI_APP_TOKEN", "a" * 40)
    monkeypatch.setenv("GLPI_USER_TOKEN", "b" * 50)
    try:
        validate_glpi_tokens()
    except SystemExit:
        pytest.fail("validate_glpi_tokens raised SystemExit unexpectedly")
