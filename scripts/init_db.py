import argparse
import asyncio
import logging
import sys

from glpi_dashboard.data.database import init_db


async def _run(drop_all: bool) -> None:
    await init_db(drop_all=drop_all)


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize PostgreSQL schema from schema.sql")
    parser.add_argument(
        "--drop-all",
        action="store_true",
        help="Drop all tables before creating",
    )
    args = parser.parse_args()

    try:
        asyncio.run(_run(drop_all=args.drop_all))
    except Exception as e:  # noqa: BLE001
        logging.error(e)
        sys.exit(1)

    print("\u2714 Database initialized")
    sys.exit(0)


if __name__ == "__main__":
    main()
