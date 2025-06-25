import argparse
import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path
from glpi_session import GLPISession, Credentials

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from config import (
    GLPI_BASE_URL,
    GLPI_APP_TOKEN,
    GLPI_USERNAME,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
)
from data_pipeline import process_raw, save_json


async def fetch_and_save(
    output: Path = Path("mock/sample_data.json"),
    status: str | None = None,
    limit: int = 100,
) -> None:
    """Fetch tickets from GLPI and save them to a JSON file."""
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    session = GLPISession(GLPI_BASE_URL, creds)
    criteria = []
    if status is not None:
        criteria.append({"field": "status", "searchtype": "equals", "value": status})
    async with session as client:
        tickets = await client.get(
            "search/Ticket",
            params={"criteria": criteria, "range": f"0-{limit-1}"},
        )
    tickets = tickets.get("data", tickets)
    df = process_raw(tickets)
    save_json(df, str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch tickets from GLPI API")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("mock/sample_data.json"),
        help="Path to save JSON data",
    )
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum results",
    )
    args = parser.parse_args()

    asyncio.run(fetch_and_save(output=args.output, status=args.status, limit=args.limit))
    print(f"✔ Saved tickets to {args.output}")


if __name__ == "__main__":
    main()
