from sqlalchemy.orm import Session
from dishka import Provider, make_async_container, Scope
from dishka.integrations.fastapi import setup_dishka

from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyOrderRepository,
)


def create_container(session: Session):
    provider = Provider()
    repo = SqlAlchemyOrderRepository(session)

    def get_repo() -> OrderRepository:
        return repo

    provider.provide(get_repo, scope=Scope.APP)
    return make_async_container(provider)


def init_fastapi_app(app, session: Session) -> None:
    """Attach Dishka container to FastAPI app."""
    container = create_container(session)
    setup_dishka(container, app)
