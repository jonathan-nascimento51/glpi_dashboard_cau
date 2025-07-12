import pytest

from backend.application.events_consumer import TicketEventConsumer
from backend.application.metrics_worker import update_metrics
from shared.utils.redis_client import RedisClient


class DummyCache(RedisClient):
    """A mock cache that conforms to the RedisClient interface for tests."""

    def __init__(self):
        # Avoid RedisClient's __init__ which may attempt to connect.
        self._client = None
        self.hits = 0
        self.misses = 0
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value: object, ttl_seconds: int | None = None):
        self.data[key] = value

    async def _connect(self) -> None:
        # This dummy doesn't need a real connection.
        pass


@pytest.mark.asyncio
async def test_update_metrics_writes_cache():
    cache = DummyCache()
    ticket = {"id": 1, "status": 1, "priority": 2, "date_creation": "2024-06-01"}
    await update_metrics({"cache": cache}, ticket)
    assert cache.data["tickets_api"][0]["id"] == 1
    assert "metrics_aggregated" in cache.data


@pytest.mark.asyncio
async def test_consumer_processes_events():
    events = [
        {
            "type": "TicketCreated",
            "payload": {
                "id": 2,
                "status": 2,
                "priority": 3,
                "date_creation": "2024-06-02",
            },
        }
    ]

    async def source():
        for e in events:
            yield e

    cache = DummyCache()
    consumer = TicketEventConsumer(lambda: source(), cache=cache)
    await consumer.run()
    assert cache.data["tickets_api"][0]["id"] == 2
