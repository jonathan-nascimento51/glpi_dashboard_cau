# Data Pipeline Usage

## Context
The worker service ingests GLPI tickets and events, transforming them into a
pandas DataFrame for analytics. The pipeline normalizes fields like status and
technician to keep metrics consistent.

## Decision
Implement the pipeline in `backend/utils/pipeline.py` using async functions. It
pulls pages from the GLPI API through `glpi_session`, converts them to DataFrame
rows and writes the final result to SQLite.

## Consequences
Analytics operate on a clean schema independent of API quirks. The pipeline must
run periodically to update the dashboard, so scheduling and error handling are
required.

## Steps
1. Configure environment variables for GLPI connection as described in the
   `glpi-session` cookbook.
2. Call `pipeline.fetch_all_tickets()` inside a background worker to produce the
   normalized DataFrame.
3. Persist the DataFrame to `data/db.sqlite` and expose it via the API layer for
   the front end.
