from dataclasses import dataclass
from uuid import UUID
from typing import List

from app.domain.value_objects.money import Money


@dataclass(frozen=True)
class CreateOrderCommand:
    order_id: UUID
    user_id: UUID
    items: List[Money]
