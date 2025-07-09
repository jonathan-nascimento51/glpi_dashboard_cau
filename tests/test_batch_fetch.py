import asyncio
import json
import time

import pytest

from src.backend.services import batch_fetch


class DummySession:
    def __init__(self, delay: float = 0.01) -> None:
        self.delay = delay

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, endpoint: str, params=None, headers=None):
        await asyncio.sleep(self.delay)
        ticket_id = int(endpoint.split("/")[-1])
        return {"data": {"id": ticket_id}}


@pytest.mark.asyncio
async def test_fetch_all_tickets(monkeypatch):
    monkeypatch.setattr(batch_fetch, "GLPISession", lambda *a, **k: DummySession())
    ids = [1, 2, 3]
    data = await batch_fetch.fetch_all_tickets(ids)
    assert [d["id"] for d in data] == ids


@pytest.mark.asyncio
async def test_async_vs_sync_benchmark(monkeypatch):
    monkeypatch.setattr(batch_fetch, "GLPISession", lambda *a, **k: DummySession())
    ids = list(range(20))

    start = time.perf_counter()
    async_result = await batch_fetch.fetch_all_tickets(ids)
    async_duration = time.perf_counter() - start

    async def sequential() -> list[dict]:
        async with DummySession() as sess:
            out = []
            for tid in ids:
                resp = await sess.get(f"Ticket/{tid}")
                out.append(resp["data"])
            return out

    start = time.perf_counter()
    sync_result = await sequential()
    sync_duration = time.perf_counter() - start

    assert async_result == sync_result
    assert async_duration < sync_duration


@pytest.mark.asyncio
async def test_fetch_all_tickets_tool_error(monkeypatch):
    async def boom(_ids):
        raise RuntimeError("fail")

    monkeypatch.setattr(batch_fetch, "fetch_all_tickets", boom)
    out = await batch_fetch.fetch_all_tickets_tool(
        batch_fetch.BatchFetchParams(ids=[1])
    )
    data = json.loads(out)
    assert data["error"]["details"] == "fail"
