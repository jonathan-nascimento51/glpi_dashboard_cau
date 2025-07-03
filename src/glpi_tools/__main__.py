"""Command-line utilities for GLPI REST API."""

from __future__ import annotations

import asyncio
import csv
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from glpi_dashboard.config import settings
from glpi_dashboard.services.glpi_rest_client import GLPIClient


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
        client = GLPIClient(
            settings.GLPI_BASE_URL,
            app_token=settings.GLPI_APP_TOKEN,
            user_token=settings.GLPI_USER_TOKEN,
        )
        await client.init_session()
        try:
            data = await client.list_search_options(itemtype)
        finally:
            await client.close()
        return data

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


if __name__ == "__main__":  # pragma: no cover
    cli()
