import argparse
import asyncio

from database import init_db


async def _run(drop_all: bool) -> None:
    await init_db(drop_all=drop_all)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize PostgreSQL schema from schema.sql"
    )
    parser.add_argument(
        "--drop-all",
        action="store_true",
        help="Drop all tables before creating",
    )
    args = parser.parse_args()

    asyncio.run(_run(drop_all=args.drop_all))
    print("\u2714 Database initialized")


if __name__ == "__main__":
    main()
