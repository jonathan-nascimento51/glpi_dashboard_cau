import importlib

import pytest


def test_simple_cache_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CACHE_TYPE", "simple")
    import backend.utils.cache as cache_module

    importlib.reload(cache_module)
    config: dict[str, object] | None = cache_module.cache.config
    assert isinstance(config, dict) and config.get("CACHE_TYPE") == "SimpleCache"


def test_redis_failure_fallback(monkeypatch: pytest.MonkeyPatch):
    class DummyReadClient:
        def ping(self):
            raise Exception("fail")

    class DummyBackend:
        def __init__(self):
            self._read_client = DummyReadClient()

    class DummyCache:
        def __init__(self, config: dict[str, object] | None = None):
            self.config = config
            self.cache = DummyBackend()

    monkeypatch.setattr("flask_caching.Cache", DummyCache)
    monkeypatch.delenv("CACHE_TYPE", raising=False)
    import backend.utils.cache as cache_module

    importlib.reload(cache_module)
    config: dict[str, object] | None = cache_module.cache.config
    assert config is not None and config["CACHE_TYPE"] == "SimpleCache"
