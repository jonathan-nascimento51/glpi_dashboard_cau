"""Kafka/RabbitMQ consumer for ticket events."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterable, Callable
from typing import Any, Dict, Optional

from backend.core.settings import EVENT_BROKER_URL
from backend.services.metrics_worker import update_metrics
from backend.utils.redis_client import RedisClient, redis_client

logger = logging.getLogger(__name__)


async def kafka_event_source(
    topic: str, bootstrap_servers: str
) -> AsyncIterable[Dict[str, Any]]:
    """Yield events from Kafka if ``aiokafka`` is available."""
    try:
        from aiokafka import AIOKafkaConsumer  # type: ignore[import-unresolved]
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("aiokafka required for Kafka consumer") from exc

    consumer = AIOKafkaConsumer(topic, bootstrap_servers=bootstrap_servers)
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                yield json.loads(msg.value)
            except (
                json.JSONDecodeError
            ) as exc:  # pragma: no cover - guard against bad payloads
                logger.error("Invalid JSON payload: %s", exc)
    finally:
        await consumer.stop()


class TicketEventConsumer:
    """Consume ticket events and update the Redis read model."""

    def __init__(
        self,
        event_source: Callable[[], AsyncIterable[Dict[str, Any]]],
        cache: Optional[RedisClient] = None,
    ) -> None:
        self.event_source = event_source
        self.cache = cache or redis_client

    async def run(self) -> None:
        async for event in self.event_source():
            await self.handle_event(event)

    async def handle_event(self, event: Dict[str, Any]) -> None:
        event_type = event.get("type")
        payload = event.get("payload", {})
        if event_type not in {"TicketCreated", "TicketUpdated"}:
            logger.debug("Skipping unknown event type: %s", event_type)
            return
        await update_metrics(payload, self.cache)


async def start_default_consumer(
    topic: str = "tickets",
) -> None:  # pragma: no cover - manual run
    """Start consumer using ``EVENT_BROKER_URL``."""

    def source() -> AsyncIterable[Dict[str, Any]]:
        return kafka_event_source(topic, EVENT_BROKER_URL)

    consumer = TicketEventConsumer(source)
    await consumer.run()


if __name__ == "__main__":  # pragma: no cover - manual run
    asyncio.run(start_default_consumer())
