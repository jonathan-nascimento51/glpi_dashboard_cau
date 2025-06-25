"""Command-line interface for collecting ticket assignments."""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv

import asyncio
from glpi_session import GLPISession, Credentials
from config import (
    GLPI_BASE_URL,
    GLPI_APP_TOKEN,
    GLPI_USERNAME,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
)
from src.etl.tickets_groups import collect_tickets_with_groups


@click.command()
@click.option("--since", required=True, help="Start date YYYY-MM-DD")
@click.option("--until", required=True, help="End date YYYY-MM-DD")
@click.option("--outfile", type=Path, help="Output Parquet file")
@click.option("--log-level", default="INFO", help="Logging level")
def main(since: str, until: str, outfile: Path | None, log_level: str) -> None:
    """Run the tickets+groups ETL pipeline."""

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    load_dotenv()

    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    client = GLPISession(GLPI_BASE_URL, creds)
    df = asyncio.run(collect_tickets_with_groups(since, until, client=client))
    if outfile is None:
        ts = dt.date.today().strftime("%Y%m%d")
        outfile = Path("datasets") / f"tickets_groups_{ts}.parquet"
    outfile.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(outfile, index=False)
    logging.info("Saved %s", outfile)


if __name__ == "__main__":  # pragma: no cover
    main()
