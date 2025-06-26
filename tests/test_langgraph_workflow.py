import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))  # noqa: E402

from src import langgraph_workflow


@pytest.mark.asyncio
async def test_workflow_fetch(monkeypatch):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return {
                "data": [
                    {
                        "id": 1,
                        "status": "new",
                        "group": "N1",
                        "date_creation": "2024-01-01",
                        "assigned_to": "alice",
                    }
                ]
            }

    monkeypatch.setattr(langgraph_workflow, "GLPISession", lambda *a, **k: FakeSession())

    workflow = langgraph_workflow.build_workflow().compile()
    state = {"messages": ["fetch"], "next_agent": "", "iteration_count": 0}
    result = await workflow.ainvoke(state)
    assert "fetched tickets" in result["messages"]
