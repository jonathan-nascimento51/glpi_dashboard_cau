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
