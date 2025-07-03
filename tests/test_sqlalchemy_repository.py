from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.sqlalchemy_repository import (
    Base,
    SqlAlchemyOrderRepository,
)
from app.domain.entities.order import Order
from app.domain.value_objects.money import Money


def test_save_and_get() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    repo = SqlAlchemyOrderRepository(session)
    order = Order(uuid4(), uuid4())
    order.add_item(Money(Decimal("10"), "USD"))
    repo.save(order)
    retrieved = repo.get_by_id(order.order_id)
    assert retrieved is not None
    assert retrieved.total().amount == Decimal("10")
