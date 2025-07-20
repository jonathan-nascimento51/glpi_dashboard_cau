"""Observer pattern for order finalization events."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Protocol

from shared.utils.logging import init_logging

logger = logging.getLogger(__name__)


@dataclass
class Order:
    id: int
    finalized: bool = False
    _observers: List["Observer"] = field(default_factory=list)

    def register(self, observer: "Observer") -> None:
        self._observers.append(observer)

    def finalize(self) -> None:
        self.finalized = True
        for obs in list(self._observers):
            obs.update(self)


class Observer(Protocol):
    def update(self, order: Order) -> None: ...


class EmailNotifier:
    def update(self, order: Order) -> None:
        logger.info("Email sent for order %s", order.id)


class InventoryUpdater:
    def update(self, order: Order) -> None:
        logger.info("Inventory updated for order %s", order.id)


class LogisticsScheduler:
    def update(self, order: Order) -> None:
        logger.info("Logistics scheduled for order %s", order.id)


if __name__ == "__main__":
    init_logging()

    order = Order(1)
    order.register(EmailNotifier())
    order.register(InventoryUpdater())
    order.register(LogisticsScheduler())
    order.finalize()
