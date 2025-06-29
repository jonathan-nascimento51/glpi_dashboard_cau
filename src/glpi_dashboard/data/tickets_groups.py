"""Re-export tickets and groups ETL helpers for backwards compatibility."""

from src.etl import tickets_groups as _tg
import asyncio
import datetime as dt

collect_tickets_with_groups = _tg.collect_tickets_with_groups
save_parquet = _tg.save_parquet
Path = _tg.Path


def pipeline(start: str, end: str, outfile: str | None = None) -> Path:
    """Collect data and persist to ``datasets`` directory."""
    outfile = outfile or f"datasets/tickets_groups_{dt.date.today():%Y%m%d}.parquet"
    df = asyncio.run(collect_tickets_with_groups(start, end))
    return save_parquet(df, outfile)


__all__ = [
    "collect_tickets_with_groups",
    "save_parquet",
    "Path",
    "pipeline",
]
