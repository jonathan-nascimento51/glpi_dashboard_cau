import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy import Column, Integer, DateTime, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import SQLAlchemyError

from glpi_dashboard.config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()

# Resolve schema.sql path relative to project root
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema.sql"


class Ticket(Base):
    """SQLAlchemy model for raw GLPI ticket data."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    glpi_ticket_id = Column(Integer, unique=True, nullable=False)
    raw_data = Column(JSONB, nullable=False)
    status = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False)
    assignee_id = Column(
        Integer, nullable=True
    )  # Assuming this maps to a user/group ID
    opened_at = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), default=datetime.now)

    def __repr__(self):
        return (
            f"<Ticket(glpi_ticket_id={self.glpi_ticket_id}, "
            f"status={self.status}, priority={self.priority})>"
        )


# Async engine for SQLAlchemy 2.0
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db(drop_all: bool = False) -> None:
    """
    Initializes the database schema by executing schema.sql.
    If drop_all is True, drops all tables and materialized views before recreating.
    """
    async with engine.begin() as conn:
        if drop_all:
            logger.info("Dropping all existing tables and materialized views...")
            # Drop materialized view first due to potential dependencies
            await conn.execute(
                text("DROP MATERIALIZED VIEW IF EXISTS mv_ticket_summary CASCADE;")
            )
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("All tables dropped.")

        logger.info("Creating database schema from schema.sql...")
        # Read and execute schema.sql from repository root
        with SCHEMA_PATH.open("r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Split by semicolon to execute multiple statements
        for statement in schema_sql.split(";"):
            stripped_statement = statement.strip()
            if stripped_statement:
                try:
                    await conn.execute(text(stripped_statement))
                except Exception as e:
                    # Log error but continue unless the failure is critical
                    logger.error(
                        "Error executing SQL statement: "
                        f"{stripped_statement[:100]}... Error: {e}"
                    )

        logger.info("Database schema initialization complete.")


async def insert_tickets(tickets_data: List[Dict[str, Any]]) -> None:
    """
    Inserts or updates ticket data into the 'tickets' table.
    Uses ON CONFLICT DO UPDATE to handle existing tickets based on glpi_ticket_id.
    """
    if not tickets_data:
        return

    async with AsyncSessionLocal() as session:
        try:
            values_clauses: List[str] = []
            params = {}
            for i, ticket_dict in enumerate(tickets_data):
                # Extract relevant fields for the 'tickets' table
                glpi_ticket_id = ticket_dict.get("id")
                status = ticket_dict.get("status")
                priority = ticket_dict.get("priority")
                # Assuming 'users_id_assign' is the assignee ID in GLPI ticket data
                assignee_id = ticket_dict.get("users_id_assign")
                # GLPI date_creation is ISO 8601 datetime string
                opened_at_str = ticket_dict.get("date_creation")
                opened_at = (
                    datetime.fromisoformat(opened_at_str) if opened_at_str else None
                )

                if not all([glpi_ticket_id, status, priority, opened_at]):
                    logger.warning(
                        "Skipping ticket due to missing essential data: "
                        f"{ticket_dict.get('id')}"
                    )
                    continue

                values_clauses.append(
                    f"(:glpi_ticket_id_{i}, :raw_data_{i}, :status_{i}, "
                    f":priority_{i}, :assignee_id_{i}, :opened_at_{i})"
                )
                params[f"glpi_ticket_id_{i}"] = glpi_ticket_id
                params[f"raw_data_{i}"] = ticket_dict
                params[f"status_{i}"] = status
                params[f"priority_{i}"] = priority
                params[f"assignee_id_{i}"] = assignee_id
                params[f"opened_at_{i}"] = opened_at

            if not values_clauses:
                logger.info("No valid tickets to insert/update.")
                return

            insert_stmt = f"""
            INSERT INTO tickets (
                glpi_ticket_id, raw_data, status, priority, assignee_id, opened_at
            )
            VALUES {', '.join(values_clauses)}
            ON CONFLICT (glpi_ticket_id) DO UPDATE SET
                raw_data = EXCLUDED.raw_data,
                status = EXCLUDED.status,
                priority = EXCLUDED.priority,
                assignee_id = EXCLUDED.assignee_id,
                opened_at = EXCLUDED.opened_at,
                ingested_at = CURRENT_TIMESTAMP;
            """
            await session.execute(text(insert_stmt), params)
            await session.commit()
            logger.info(
                "Successfully inserted/updated %d tickets into PostgreSQL",
                len(tickets_data),
            )
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error during ticket insertion: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"An unexpected error occurred during ticket insertion: {e}")
            raise


async def refresh_materialized_view() -> float:
    """
    Refreshes the mv_ticket_summary materialized view concurrently.
    Logs the time taken for the refresh.
    [3, 7]
    """
    start_time = time.monotonic()
    async with AsyncSessionLocal() as session:
        try:
            logger.info(
                "Refreshing materialized view mv_ticket_summary CONCURRENTLY..."
            )
            await session.execute(
                text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ticket_summary;")
            )
            await session.commit()
            end_time = time.monotonic()
            refresh_duration = end_time - start_time
            logger.info(
                f"Materialized view refreshed in {refresh_duration:.2f} seconds."
            )
            return refresh_duration
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error refreshing materialized view: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(
                f"An unexpected error occurred during materialized view refresh: {e}"
            )
            raise
