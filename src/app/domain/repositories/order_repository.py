from __future__ import annotations

import abc
from typing import Optional
from uuid import UUID

from app.domain.entities.order import Order


class OrderRepository(abc.ABC):
    """Repository interface for Orders."""

    @abc.abstractmethod
    def save(self, order: Order) -> None:
        """Persist an order."""

    @abc.abstractmethod
    def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Retrieve an order by its ID."""
