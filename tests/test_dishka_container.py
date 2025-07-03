from decimal import Decimal
from uuid import UUID, uuid4

from dishka import Provider, Scope, make_async_container

from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository
from app.domain.value_objects.money import Money


class DummyRepo(OrderRepository):
    def __init__(self) -> None:
        self._order = Order(uuid4(), uuid4(), [Money(Decimal("1"), "USD")])

    def save(self, order: Order) -> None:
        self._order = order

    def get_by_id(self, order_id: UUID) -> Order:
        return self._order


def test_override_repository() -> None:
    repo = DummyRepo()
    provider = Provider()

    def get_repo() -> OrderRepository:
        return repo

    provider.provide(get_repo, scope=Scope.APP)
    container = make_async_container(provider)

    async def run() -> None:
        resolved = await container.get(OrderRepository)
        assert resolved is repo

    import asyncio

    asyncio.run(run())
