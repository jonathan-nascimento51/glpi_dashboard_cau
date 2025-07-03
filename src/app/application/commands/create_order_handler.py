from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository
from .create_order_command import CreateOrderCommand


class CreateOrderHandler:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def handle(self, command: CreateOrderCommand) -> Order:
        order = Order(command.order_id, command.user_id, list(command.items))
        self._repository.save(order)
        return order
