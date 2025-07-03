from dataclasses import dataclass, field
from uuid import UUID
from decimal import Decimal
from typing import List

from app.domain.value_objects.money import Money


@dataclass
class Order:
    order_id: UUID
    user_id: UUID
    items: List[Money] = field(default_factory=list)

    def add_item(self, item: Money) -> None:
        self.items.append(item)

    def total(self) -> Money:
        if not self.items:
            return Money(Decimal("0"), "USD")
        currency = self.items[0].currency
        total_amount = sum((i.amount for i in self.items), Decimal("0"))
        return Money(total_amount, currency)
