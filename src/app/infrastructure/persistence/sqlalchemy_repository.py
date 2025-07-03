from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column, String, Numeric, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.domain.entities.order import Order
from app.domain.value_objects.money import Money
from app.domain.repositories.order_repository import OrderRepository

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, order: Order) -> None:
        total = order.total()
        model = OrderModel(
            id=str(order.order_id),
            user_id=str(order.user_id),
            total_amount=total.amount,
            currency=total.currency,
        )
        self.session.merge(model)
        self.session.commit()

    def get_by_id(self, order_id: UUID) -> Order | None:
        model = self.session.get(OrderModel, str(order_id))
        if model is None:
            return None
        money = Money(Decimal(model.total_amount), model.currency)
        return Order(UUID(model.id), UUID(model.user_id), [money])


def get_sqlite_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
