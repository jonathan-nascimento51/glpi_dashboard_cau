# Data Pipeline Usage

## Context
The worker process fetches ticket data from GLPI and normalizes it before the dashboard consumes it. Keeping the pipeline modular helps when adding new metrics or data sources.

## Decision
Implement `backend/utils/pipeline.py` to transform raw API responses into a pandas DataFrame. Each function handles a single responsibility such as filtering, aggregation or export.

## Consequences
Data transformations remain reproducible and testable. The dashboard receives clean structures instead of mixing business logic into the UI layer.

## Steps
1. Fetch data through `glpi_session.get_tickets()`.
2. Pass the list of dictionaries to `process_raw()` to build a DataFrame.
3. Use helper functions for calculations like SLA breach counts.
4. Save intermediate data to JSON for debugging or offline previews.
