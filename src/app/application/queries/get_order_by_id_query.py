from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetOrderByIdQuery:
    order_id: UUID
