"""Command-line interface for collecting ticket assignments."""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv

from src.api.glpi_api import GLPIClient
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

    client = GLPIClient()
    df = collect_tickets_with_groups(since, until, client=client)
    if outfile is None:
        outfile = (
            Path("datasets")
            / f"tickets_groups_{dt.date.today().strftime('%Y%m%d')}.parquet"
        )
    outfile.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(outfile, index=False)
    logging.info("Saved %s", outfile)


if __name__ == "__main__":
    main()
