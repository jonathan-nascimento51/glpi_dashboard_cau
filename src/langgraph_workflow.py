"""LangGraph workflow for GLPI data operations."""

from __future__ import annotations

from typing import List, Optional, TypedDict

import pandas as pd
from langgraph.graph import END, StateGraph

from glpi_dashboard.config.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from glpi_dashboard.data.pipeline import process_raw
from glpi_dashboard.services.glpi_session import Credentials, GLPISession


class AgentState(TypedDict, total=False):
    """Simple state container shared across agents."""

    messages: List[str]
    next_agent: str
    iteration_count: int
    data: Optional[pd.DataFrame]


# --------------------------- Specialist Nodes ---------------------------


def supervisor(state: AgentState) -> AgentState:
    """Route to the next specialist based on the last message."""
    last = state["messages"][-1]
    if "fetch" in last:
        state["next_agent"] = "fetcher"
    elif "analyze" in last:
        state["next_agent"] = "analyzer"
    else:
        state["next_agent"] = "fallback"
    state["iteration_count"] += 1
    return state


async def fetcher(state: AgentState) -> AgentState:
    """Fetch tickets from the GLPI API and store as dataframe."""
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    async with GLPISession(GLPI_BASE_URL, creds) as client:
        tickets = await client.get("search/Ticket")
    df = process_raw(tickets.get("data", tickets))
    state["data"] = df
    state["messages"].append("fetched tickets")
    return state


def analyzer(state: AgentState) -> AgentState:
    """Compute simple metrics from dataframe."""
    df = state.get("data")
    if df is None:
        state["messages"].append("no data to analyze")
    else:
        metrics = {
            "total": len(df),
            "opened": int((df["status"] != "closed").sum()),
            "closed": int((df["status"] == "closed").sum()),
        }
        state["messages"].append(f"metrics: {metrics}")
    return state


def fallback(state: AgentState) -> AgentState:
    """Default node for unrecognized commands."""
    state["messages"].append("command not recognized")
    return state


# --------------------------- Workflow Builder ---------------------------


def build_workflow() -> StateGraph:
    """Create LangGraph workflow with supervisor and workers."""
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor)
    workflow.add_node("fetcher", fetcher)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("fallback", fallback)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda s: s["next_agent"],
        {
            "fetcher": "fetcher",
            "analyzer": "analyzer",
            "fallback": "fallback",
        },
    )

    workflow.add_edge("fetcher", "analyzer")
    workflow.add_edge("analyzer", "fallback")
    workflow.add_edge("fallback", END)

    return workflow


__all__ = [
    "AgentState",
    "supervisor",
    "fetcher",
    "analyzer",
    "fallback",
    "build_workflow",
]
