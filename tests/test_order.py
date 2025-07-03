from decimal import Decimal
from uuid import uuid4

from app.domain.entities.order import Order
from app.domain.value_objects.money import Money


def test_total_calculation() -> None:
    order = Order(uuid4(), uuid4())
    order.add_item(Money(Decimal("10"), "USD"))
    order.add_item(Money(Decimal("5"), "USD"))
    total = order.total()
    assert total.amount == Decimal("15")
    assert total.currency == "USD"
