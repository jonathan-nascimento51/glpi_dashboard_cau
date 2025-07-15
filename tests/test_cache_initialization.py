import importlib


def test_simple_cache_env(monkeypatch):
    monkeypatch.setenv("CACHE_TYPE", "simple")
    import backend.utils.cache as cache_module

    importlib.reload(cache_module)
    assert cache_module.cache.config["CACHE_TYPE"] == "SimpleCache"


def test_redis_failure_fallback(monkeypatch):
    class DummyReadClient:
        def ping(self):
            raise Exception("fail")

    class DummyBackend:
        def __init__(self):
            self._read_client = DummyReadClient()

    class DummyCache:
        def __init__(self, config=None):
            self.config = config
            self.cache = DummyBackend()

    monkeypatch.setattr("flask_caching.Cache", DummyCache)
    monkeypatch.delenv("CACHE_TYPE", raising=False)
    import backend.utils.cache as cache_module

    importlib.reload(cache_module)
    assert cache_module.cache.config["CACHE_TYPE"] == "SimpleCache"
