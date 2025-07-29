"""Command-line utilities for GLPI REST API."""

from __future__ import annotations

import asyncio
import csv
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from backend.core.settings import settings
from backend.infrastructure.glpi.glpi_session import Credentials, GLPISession


@click.group()
def cli() -> None:
    """Utility commands for interacting with GLPI."""


@cli.command("list-fields")
@click.argument("itemtype")
@click.option("--csv", "csv_path", type=Path, help="Export results to CSV")
def list_fields(itemtype: str, csv_path: Path | None) -> None:
    """List search fields for ``ITEMTYPE``.

    Examples:
        python -m glpi_tools list-fields Ticket
        python -m glpi_tools list-fields User --csv fields.csv
    """

    load_dotenv()

    async def _run() -> dict:
        creds = Credentials(
            app_token=settings.GLPI_APP_TOKEN,
            user_token=settings.GLPI_USER_TOKEN,
        )
        async with GLPISession(settings.GLPI_BASE_URL, creds) as client:
            return await client.list_search_options(itemtype)

    data = asyncio.run(_run())
    options = data.get("data", data)
    rows: list[tuple[str, str, str]] = []
    if isinstance(options, dict):
        keys = sorted(options, key=lambda x: int(x))
        for idx in keys:
            info = options[idx]
            name = str(info.get("name", ""))
            dtype = str(info.get("datatype", ""))
            rows.append((str(idx), name, dtype))
    elif isinstance(options, list):
        for field in options:
            idx = str(field.get("id", ""))
            name = str(field.get("name", ""))
            dtype = str(field.get("datatype", ""))
            rows.append((idx, name, dtype))
    else:
        raise SystemExit("Unexpected response format")

    table = Table(title=f"Fields for {itemtype}")
    table.add_column("Index", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Datatype")
    for idx, name, dtype in rows:
        table.add_row(idx, name, dtype)

    Console().print(table)

    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["index", "name", "datatype"])
            writer.writerows(rows)
        Console().print(f"Saved CSV to {csv_path}")


import click

@cli.command("count-by-level")
@click.argument("levels", nargs=-1)
def count_by_level(levels: tuple[str]) -> None:
    """Show ticket status counts for one or more ``LEVELS``."""

    if not levels:
        raise click.UsageError("Specify at least one level")

    load_dotenv()

    async def _run() -> dict[str, dict[str, int]]:
        creds = Credentials(
            app_token=settings.GLPI_APP_TOKEN,
            user_token=settings.GLPI_USER_TOKEN,
        )
        async with GLPISession(settings.GLPI_BASE_URL, creds) as session:
            from backend.application.glpi_api_client import GlpiApiClient

            client = GlpiApiClient(session=session)
            return await client.get_status_counts_by_levels(list(levels))

    data = asyncio.run(_run())

    table = Table(title="Status counts by level")
    table.add_column("Level", style="cyan")
    table.add_column("New", justify="right")
    table.add_column("Pending", justify="right")
    table.add_column("Solved", justify="right")

    for lvl in levels:
        counts = data.get(lvl, {})
        table.add_row(
            lvl,
            str(counts.get("new", 0)),
            str(counts.get("pending", 0)),
            str(counts.get("solved", 0)),
        )

    Console().print(table)


if __name__ == "__main__":  # pragma: no cover
    cli()
