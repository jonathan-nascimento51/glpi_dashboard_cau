"""LangGraph workflow for GLPI data operations."""

# mypy: ignore-errors

from __future__ import annotations

import ast
import tempfile
from enum import Enum
from pathlib import Path
from typing import List, Optional, TypedDict

import pandas as pd
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from backend.core.settings import (
    GLPI_APP_TOKEN,
    GLPI_BASE_URL,
    GLPI_PASSWORD,
    GLPI_USER_TOKEN,
    GLPI_USERNAME,
)
from backend.utils import sanitize_message
from glpi_dashboard.acl import process_raw

from .glpi_session import Credentials, GLPISession


def create_structured_output_runnable(
    prompt: PromptTemplate, llm: FakeListLLM, model: type[BaseModel]
) -> Runnable:
    """Return a runnable that validates LLM output as a Pydantic model."""
    parser = PydanticOutputParser(pydantic_object=model)
    return prompt | llm | parser


class AgentState(TypedDict):
    """Simple state container shared across agents."""

    messages: List[str]
    next_agent: str
    iteration_count: int
    data: Optional[pd.DataFrame]
    error: Optional[str]


class NextAgent(BaseModel):
    """Structured output deciding the next node."""

    next_agent: str = Field(..., description="Name of the next agent to execute")


class TicketStatus(str, Enum):
    """Allowed GLPI ticket statuses."""

    NEW = "new"
    ASSIGNED = "assigned"
    PLANNED = "planned"
    WAITING = "waiting"
    SOLVED = "solved"
    CLOSED = "closed"


class FetcherArgs(BaseModel):
    """Input parameters for the fetcher node."""

    status: TicketStatus | None = Field(
        default=None, description="Optional status filter for tickets"
    )
    limit: int = Field(50, description="Maximum number of tickets to fetch")


class Metrics(BaseModel):
    """Validated metrics produced by the analyzer."""

    total: int
    opened: int
    closed: int


AVAILABLE_AGENTS = ["fetcher", "analyzer", "fallback"]
"""Agents that can be dynamically routed by the supervisor."""


SUPERVISOR_PROMPT = PromptTemplate(
    template=(
        "You are a supervisor deciding which agent should act next.\n"
        "Available agents: {options}.\n"
        "Given the latest user message: '{message}' return a JSON object with "
        "the key 'next_agent'.\n"
        "Examples:\n"
        '- message: \'fetch latest tickets\' -> {{"next_agent": "fetcher"}}\n'
        '- message: \'show stats\' -> {{"next_agent": "analyzer"}}'
    ),
    input_variables=["message", "options"],
)

# Using FakeListLLM to keep tests deterministic. The static response ensures
# that unit tests route execution to the ``fetcher`` node. In production this
# could be replaced by any chat model compatible with LangChain.
llm = FakeListLLM(responses=['{"next_agent": "fetcher"}'])

# create_structured_output_runnable converts the LLM and prompt to a Runnable
# that outputs a Pydantic model.
supervisor_llm = create_structured_output_runnable(SUPERVISOR_PROMPT, llm, NextAgent)


# --------------------------- Specialist Nodes ---------------------------


def supervisor(state: AgentState) -> AgentState:
    """Use an LLM to decide which worker should run next."""
    last = sanitize_message(state["messages"][-1])
    opts = ", ".join(AVAILABLE_AGENTS)
    # Allow previous nodes to set ``next_agent`` explicitly.
    if not state.get("next_agent"):
        model = supervisor_llm.invoke({"message": last, "options": opts})
        state["next_agent"] = model.next_agent
    state["iteration_count"] += 1
    return state


async def fetcher(state: AgentState, args: FetcherArgs | None = None) -> AgentState:
    """Fetch tickets from the GLPI API and store as dataframe.

    Parameters
    ----------
    state:
        Current workflow state which will be mutated.
    args:
        Optional :class:`FetcherArgs` specifying filters.
    """
    args = args or FetcherArgs()
    creds = Credentials(
        app_token=GLPI_APP_TOKEN,
        user_token=GLPI_USER_TOKEN,
        username=GLPI_USERNAME,
        password=GLPI_PASSWORD,
    )
    async with GLPISession(GLPI_BASE_URL, creds) as client:
        params = (
            {
                "criteria[0][field]": "status",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": args.status,
            }
            if args.status
            else None
        )
        tickets = await client.get("search/Ticket", params=params)
    df = process_raw(tickets.get("data", tickets))
    state["data"] = df
    state.setdefault("messages", []).append("fetched tickets")
    return state


fetcher.args_schema = FetcherArgs  # type: ignore[attr-defined]


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
        Metrics(**metrics)  # validate
        state["messages"].append(f"metrics: {metrics}")
    return state


analyzer.args_schema = None  # type: ignore[attr-defined]


def fallback(state: AgentState) -> AgentState:
    """Default node for unrecognized commands."""
    state["messages"].append("command not recognized")
    return state


def validation_node(state: AgentState) -> AgentState:
    """Validate that analyzer produced well-formed metrics."""
    try:
        last = state["messages"][-1]
        if last.startswith("metrics:"):
            data = ast.literal_eval(last.split("metrics:", 1)[1].strip())
            Metrics(**data)
    except Exception as exc:
        state["error"] = str(exc)
    return state


def recovery_node(state: AgentState) -> AgentState:
    """Handle errors and decide whether to retry or finish.

    If ``state['error']`` is set and the number of iterations is below three,
    the workflow will append a ``"retrying"`` message so the supervisor can
    trigger the fetcher again. Otherwise the flow falls back to the default
    node and clears the error so the graph can terminate gracefully.
    """
    if state.get("error"):
        if state.get("next_agent") and state["iteration_count"] < 3:
            state["messages"].append("retrying")
        else:
            state["next_agent"] = "fallback"
    else:
        state["next_agent"] = "fallback"
    state["error"] = None
    return state


NODE_FUNCTIONS = {
    "fetcher": fetcher,
    "analyzer": analyzer,
    "fallback": fallback,
}


# --------------------------- Workflow Builder ---------------------------


def build_workflow(path: str | None = None) -> StateGraph:
    """Create LangGraph workflow with supervisor and workers.

    Parameters
    ----------
    path:
        Optional directory to store the workflow state file. Defaults
        to the system temporary directory.
    """
    if path is None:
        path = tempfile.gettempdir()
    db_path = Path(path) / "workflow_state.sqlite"
    checkpointer = SqliteSaver(str(db_path))
    workflow = StateGraph(AgentState, checkpointer=checkpointer)

    workflow.add_node("supervisor", supervisor)
    for name in AVAILABLE_AGENTS:
        workflow.add_node(name, NODE_FUNCTIONS[name])
    workflow.add_node("validation", validation_node)
    workflow.add_node("recovery", recovery_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda s: s["next_agent"],
        {name: name for name in AVAILABLE_AGENTS},
    )

    workflow.add_edge("fetcher", "analyzer")
    workflow.add_edge("analyzer", "validation")
    workflow.add_edge("validation", "recovery")
    workflow.add_edge("recovery", "supervisor")
    workflow.add_edge("fallback", END)

    return workflow


__all__ = [
    "AgentState",
    "supervisor",
    "fetcher",
    "analyzer",
    "fallback",
    "validation_node",
    "recovery_node",
    "build_workflow",
    "GLPISession",
    "TicketStatus",
    "AVAILABLE_AGENTS",
]
