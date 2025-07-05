import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from glpi_dashboard.data import database


@pytest_asyncio.fixture()
async def sqlite_session(monkeypatch):
    import json
    import sqlite3

    sqlite3.register_adapter(dict, lambda d: json.dumps(d))
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                CREATE TABLE tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    glpi_ticket_id INTEGER UNIQUE NOT NULL,
                    raw_data TEXT NOT NULL,
                    status INTEGER NOT NULL,
                    priority INTEGER NOT NULL,
                    assignee_id INTEGER,
                    opened_at TIMESTAMP NOT NULL,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "AsyncSessionLocal", Session)
    try:
        yield Session
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_insert_tickets_sqlite(sqlite_session):
    tickets = [
        {
            "id": 1,
            "status": 2,
            "priority": 4,
            "users_id_assign": 1,
            "date_creation": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "status": 3,
            "priority": 2,
            "users_id_assign": 2,
            "date_creation": "2024-01-02T00:00:00",
        },
    ]
    await database.insert_tickets(tickets)
    async with sqlite_session() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM tickets"))
        count = result.scalar_one()
    assert count == 2


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, *args, **kwargs):
        return None

    async def commit(self):
        pass

    async def rollback(self):
        pass


class ErrorSession(DummySession):
    async def execute(self, *args, **kwargs):
        raise SQLAlchemyError("boom")


@pytest.mark.asyncio
async def test_refresh_materialized_view_duration(monkeypatch):
    monkeypatch.setattr(database, "AsyncSessionLocal", lambda: DummySession())
    duration = await database.refresh_materialized_view()
    assert isinstance(duration, float)


@pytest.mark.asyncio
async def test_refresh_materialized_view_error(monkeypatch):
    monkeypatch.setattr(database, "AsyncSessionLocal", lambda: ErrorSession())
    with pytest.raises(SQLAlchemyError):
        await database.refresh_materialized_view()
