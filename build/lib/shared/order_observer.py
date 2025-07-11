"""Observer pattern for order finalization events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol


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
        print(f"Email sent for order {order.id}")


class InventoryUpdater:
    def update(self, order: Order) -> None:
        print(f"Inventory updated for order {order.id}")


class LogisticsScheduler:
    def update(self, order: Order) -> None:
        print(f"Logistics scheduled for order {order.id}")


if __name__ == "__main__":
    order = Order(1)
    order.register(EmailNotifier())
    order.register(InventoryUpdater())
    order.register(LogisticsScheduler())
    order.finalize()
