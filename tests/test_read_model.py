import json
import sqlite3

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.infrastructure.database import database
from backend.infrastructure.database import read_model as ticket_summary


@pytest_asyncio.fixture()
async def sqlite_read_model(monkeypatch):
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
        await conn.execute(
            text(
                """
                CREATE TABLE mv_ticket_summary (
                    ticket_id INTEGER,
                    status TEXT,
                    priority TEXT,
                    group_name TEXT,
                    opened_at DATE
                )
                """
            )
        )
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "AsyncSessionLocal", Session)
    monkeypatch.setattr(ticket_summary, "AsyncSessionLocal", Session)

    async def fake_refresh() -> float:
        async with Session() as session:
            await session.execute(text("DELETE FROM mv_ticket_summary"))
            await session.execute(
                text(
                    "INSERT INTO mv_ticket_summary "
                    "(ticket_id, status, priority, group_name, opened_at) "
                    "SELECT glpi_ticket_id, status, priority, '', opened_at "
                    "FROM tickets"
                )
            )

            await session.commit()
        return 0.0

    monkeypatch.setattr(database, "refresh_materialized_view", fake_refresh)
    monkeypatch.setattr(ticket_summary, "refresh_materialized_view", fake_refresh)
    yield Session
    await engine.dispose()


@pytest.mark.asyncio
async def test_insert_propagates_to_read_model(sqlite_read_model):
    tickets = [
        {
            "id": 1,
            "status": 1,
            "priority": 2,
            "users_id_assign": None,
            "date_creation": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "status": 2,
            "priority": 3,
            "users_id_assign": None,
            "date_creation": "2024-01-02T00:00:00",
        },
    ]
    await database.insert_tickets(tickets)
    await ticket_summary.refresh_read_model()
    rows = await ticket_summary.get_ticket_summary()
    assert [r.ticket_id for r in rows] == [1, 2]
