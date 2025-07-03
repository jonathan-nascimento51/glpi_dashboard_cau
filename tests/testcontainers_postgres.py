from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.domain.entities.order import Order
from app.domain.value_objects.money import Money
from app.infrastructure.persistence.sqlalchemy_repository import (
    Base, SqlAlchemyOrderRepository)


@pytest.mark.integration
def test_save_and_get_with_postgres() -> None:
    with PostgresContainer("postgres:15") as pg:
        engine = create_engine(pg.get_connection_url(), future=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        repo = SqlAlchemyOrderRepository(session)
        order = Order(uuid4(), uuid4())
        order.add_item(Money(Decimal("7"), "USD"))
        repo.save(order)
        retrieved = repo.get_by_id(order.order_id)
        assert retrieved is not None
        assert retrieved.total().amount == Decimal("7")
