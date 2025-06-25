from __future__ import annotations

"""CLI for collecting GLPI tickets with group info."""

import logging
from datetime import datetime
from pathlib import Path
import sys

import click
from rich_click.rich_command import RichCommand

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from etl.tickets_groups import pipeline


@click.command(cls=RichCommand)
@click.option("--since", required=True, help="Start date YYYY-MM-DD")
@click.option("--until", required=True, help="End date YYYY-MM-DD")
@click.option("--outfile", type=click.Path(), help="Output Parquet file")
@click.option("--log-level", default="INFO", help="Logging level")
def main(since: str, until: str, outfile: str | None, log_level: str) -> None:
    """Collect tickets and save them to a Parquet dataset."""
    logging.basicConfig(
        level=log_level.upper(), format="%(levelname)s:%(message)s"
    )
    since_dt = datetime.fromisoformat(since)
    until_dt = datetime.fromisoformat(until)
    if until_dt <= since_dt:
        raise click.BadParameter("--until must be after --since")

    path = pipeline(since, until, outfile)
    click.echo(f"Dataset saved to {path}")


if __name__ == "__main__":  # pragma: no cover
    main()

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
