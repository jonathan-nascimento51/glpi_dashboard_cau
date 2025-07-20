import pytest

from backend.utils.pagination import paginate_items


@pytest.mark.asyncio
async def test_paginate_list_only_response():
    """Pagination should handle list responses without a dict wrapper."""

    pages = {
        0: [{"id": 1}],
        1: [{"id": 2}],
        2: [],
    }

    async def fetch_page(offset: int, page_size: int):
        return pages[offset], {}

    items = await paginate_items("ticket", fetch_page, page_size=1)

    assert items == [{"id": 1}, {"id": 2}]
