import pytest

from backend.application.metrics_worker import shutdown


class DummyCache:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_shutdown_closes_cache():
    cache = DummyCache()
    await shutdown({"cache": cache})
    assert cache.closed is True
