# LangGraph Naming Guidelines

This project coordinates multiple LLM agents using LangGraph. During prototyping some edges were labeled in Portuguese while nodes followed English identifiers. Mixed naming can hinder readability and maintainability. The following table aligns control keys and node names using snake_case English terms.

| Legacy Key | Node Identifier | Standard Name | Justification |
|-----------|----------------|--------------|--------------|
| `Pesquisador` | `researcher_node` | `researcher` | Consistent English naming avoids language mixing and simplifies conditional edge evaluation. |
| `Planejador` | `planner_node` | `planner` | Keeps edge keys and node instances aligned for easier debugging and tracing. |
| `Analisador` | `analyzer_node` | `analyzer` | Snake_case identifiers are idiomatic in Python and aid code navigation. |

Use the standardized names when adding edges:

```python
workflow.add_edge("researcher", "planner")
```

All documentation and conditional logic should reference these unified keys to prevent semantic drift.

