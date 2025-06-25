"""Deprecated helper for ticket group processing."""

from __future__ import annotations

from typing import Iterable, List


def collect_tickets_with_groups(raw: Iterable[dict]) -> List[dict]:
    """Return tickets enriched with group information.

    Parameters
    ----------
    raw : Iterable[dict]
        Raw ticket records from GLPI.

    Returns
    -------
    list[dict]
        Tickets with group metadata. Currently passthrough.
    """
    return list(raw)
