from typing import Optional

from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository
from .get_order_by_id_query import GetOrderByIdQuery


class GetOrderByIdHandler:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def handle(self, query: GetOrderByIdQuery) -> Optional[Order]:
        return self._repository.get_by_id(query.order_id)
