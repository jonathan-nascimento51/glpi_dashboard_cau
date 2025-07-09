import pytest

from backend.services.metrics_worker import update_metrics
from glpi_dashboard.events.consumer import TicketEventConsumer


class DummyCache:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ttl_seconds=None):
        self.data[key] = value


@pytest.mark.asyncio
async def test_update_metrics_writes_cache():
    cache = DummyCache()
    ticket = {"id": 1, "status": 1, "priority": 2, "date_creation": "2024-06-01"}
    await update_metrics(ticket, cache)
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
