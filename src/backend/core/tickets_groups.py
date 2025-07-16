"""Command-line interface for collecting ticket assignments."""

from __future__ import annotations

import logging
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv

from backend.application.tickets_groups import pipeline


@click.command()
@click.option("--since", required=True, help="Start date YYYY-MM-DD")
@click.option("--until", required=True, help="End date YYYY-MM-DD")
@click.option("--outfile", type=Path, help="Output Parquet file")
@click.option("--log-level", default="INFO", help="Logging level")
def main(since: str, until: str, outfile: Path | None, log_level: str) -> None:
    """Run the tickets+groups ETL pipeline."""

    load_dotenv()

    outfile_str = str(outfile) if outfile else None
    path = pipeline(since, until, outfile_str)
    logging.info("Saved %s", path)


if __name__ == "__main__":  # pragma: no cover
    main()
