"""Shared pagination helpers."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any, Awaitable, Callable, Dict, List, Tuple

logger = logging.getLogger(__name__)


async def paginate_items(
    itemtype: str,
    fetch_page: Callable[[int, int], Awaitable[Tuple[Dict[str, Any], Dict[str, str]]]],
    *,
    page_size: int = 100,
) -> List[Dict[str, Any]]:
    """Fetch and combine all items from a paginated API endpoint.

    This function repeatedly calls ``fetch_page`` with increasing offsets
    until no more items are returned or an error occurs. It's designed to
    work with APIs that use offset-based pagination and can optionally use a
    'Content-Range' header for early termination.

    Args:
        itemtype: A descriptive name for the items being fetched, used for logging.
        fetch_page: An awaitable function that accepts an offset and page size,
            and returns a tuple containing the data payload (dict) and response
            headers (dict).
        page_size: The number of items to request per page.

    Returns:
        A list of all fetched items, combined from all pages.
    """
    logger.info("Starting paginated fetch for %s", itemtype)
    results: List[Dict[str, Any]] = []
    offset = 0
    total_records: int | None = None

    while True:
        try:
            data, headers = await fetch_page(offset, page_size)
            # One-time attempt to get total records from headers for optimization
            if total_records is None:
                range_header = headers.get("Content-Range")
                if range_header and "/" in range_header:
                    with contextlib.suppress(ValueError):
                        total_records = int(range_header.split("/")[-1])
        except Exception as exc:  # pragma: no cover - network failure
            logger.critical("Pagination aborted for %s: %s", itemtype, exc)
            break

        # The API might return a single object or a list. Safely access a potential
        # 'data' key only when the payload is a dictionary.
        if isinstance(data, dict):
            page_items_raw: Any = data.get("data", data)
        else:
            page_items_raw = data

        # Normalize the raw page items into a list.
        items_list: List[Any]
        if isinstance(page_items_raw, dict):
            items_list = [page_items_raw]
        else:
            # Handle iterables (like lists) and None gracefully.
            items_list = list(page_items_raw or [])

        # Ensure all items in the list are dictionaries, filtering out other types.
        page_items: List[Dict[str, Any]] = [
            item for item in items_list if isinstance(item, dict)
        ]

        if not page_items:
            logger.info("No items in page; stopping pagination for %s", itemtype)
            break

        results.extend(page_items)
        offset += page_size
        await asyncio.sleep(0.1)

        # Stop if we've fetched all known records.
        if total_records is not None and offset >= total_records:
            logger.info(
                "Fetched %d of %d total records for %s; stopping.",
                len(results),
                total_records,
                itemtype,
            )
            break

    logger.info("Pagination finished for %s: %d items", itemtype, len(results))
    return results


__all__ = ["paginate_items"]
