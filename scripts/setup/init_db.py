import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure the src directory is on the Python path so the script can be executed
# from any working directory without manually setting PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.backend.db.database import init_db  # noqa: E402


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

    try:
        asyncio.run(_run(drop_all=args.drop_all))
    except Exception as e:  # noqa: BLE001
        logging.error(e)
        sys.exit(1)

    print("\u2714 Database initialized")
    sys.exit(0)


if __name__ == "__main__":
    main()
