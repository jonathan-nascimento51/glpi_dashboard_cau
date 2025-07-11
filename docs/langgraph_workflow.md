# LangGraph Workflow

`langgraph_workflow.py` orchestrates a small supervisor graph used by the worker service. The file defines a state machine where an LLM-driven supervisor routes execution to specialized nodes.

## Supervisor and workers

The **supervisor** node examines the latest message and decides which worker should act next. The available workers are:

- **fetcher** – retrieves tickets from the GLPI API and stores them in the shared state.
- **analyzer** – computes simple metrics from the fetched dataframe (total, opened and closed tickets).
- **validation** – verifies that the analyzer produced a well-formed result.
- **recovery** – handles errors and either retries the fetcher or falls back.
- **fallback** – default node when a command is not recognized.

The shared `AgentState` keeps the message history, fetched data and the `next_agent` key used for routing.

## Running the workflow

Compile the graph and invoke it with an initial state:

```bash
PYTHONPATH=src python - <<'PY'
from src.backend.application.langgraph_workflow import build_workflow
wf = build_workflow().compile()
state = {"messages": ["fetch"], "next_agent": "", "iteration_count": 0}
result = wf.invoke(state)
print(result["messages"][-1])
PY
```

The command prints `fetched tickets` when the supervisor routes execution to the fetcher and the API call succeeds.
