import pytest

pytest.importorskip("aiohttp")

from aiohttp import BasicAuth

import scripts.validate_credentials as vc


def test_get_auth_header_user_token(monkeypatch):
    monkeypatch.setattr(vc, "GLPI_USER_TOKEN", "tok")
    monkeypatch.setattr(vc, "GLPI_USERNAME", "")
    monkeypatch.setattr(vc, "GLPI_PASSWORD", "")
    assert vc.get_auth_header() == {"Authorization": "user_token tok"}


def test_get_auth_header_basic(monkeypatch):
    monkeypatch.setattr(vc, "GLPI_USER_TOKEN", None)
    monkeypatch.setattr(vc, "GLPI_USERNAME", "alice")
    monkeypatch.setattr(vc, "GLPI_PASSWORD", "secret")
    assert vc.get_auth_header() == {
        "Authorization": BasicAuth("alice", "secret").encode()
    }
