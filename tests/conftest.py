"""Pytest configuration for the project.

This ensures the project sources under ``src`` are available when tests are
imported as plugins and registers ``test_glpi_session`` as a plugin.
"""

import os
import sys

import pytest

# Add the ``src`` directory to ``sys.path`` so modules like ``backend`` and
# ``frontend`` are discoverable without requiring an editable install.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))


@pytest.fixture(autouse=True, scope="session")
def disable_retry_backoff_env():
    """Disable retry backoff for faster tests."""
    original = os.environ.get("DISABLE_RETRY_BACKOFF")
    os.environ["DISABLE_RETRY_BACKOFF"] = "1"
    try:
        yield
    finally:
        if original is not None:
            os.environ["DISABLE_RETRY_BACKOFF"] = original
        else:
            os.environ.pop("DISABLE_RETRY_BACKOFF", None)


@pytest.fixture(autouse=True)
def valid_tokens_env(monkeypatch: pytest.MonkeyPatch):
    """Provide valid-looking GLPI tokens for tests that require them."""
    monkeypatch.setenv("GLPI_APP_TOKEN", "a" * 40)
    monkeypatch.setenv("GLPI_USER_TOKEN", "b" * 40)
    yield
