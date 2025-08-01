# Data Pipeline Usage

## Context
The worker service ingests GLPI tickets and events, transforming them into a
pandas DataFrame for analytics. The pipeline normalizes fields like status and
technician to keep metrics consistent. It runs asynchronously to retrieve
pages in parallel and keep up with large backlogs.

## Decision
Implement the pipeline in `backend/infrastructure/glpi/normalization.py` using async functions.
It pulls pages from the GLPI API through `glpi_session`, converts them to
DataFrame rows and writes the final result to SQLite. A scheduler or cron job
should invoke the pipeline regularly to refresh metrics.

## Consequences
Analytics operate on a clean schema independent of API quirks. Because the
pipeline executes automatically, failures in fetching or parsing pages will
surface early and can be retried without blocking the dashboard.

## Steps
1. Configure environment variables for GLPI connection as described in the
   `glpi-session` cookbook.
2. Call `pipeline.fetch_all_tickets()` inside a background worker to produce the
   normalized DataFrame.
3. Persist the DataFrame to `data/db.sqlite` and expose it via the API layer for
   the front end.
4. Monitor runs via logs or metrics to catch API errors or schema changes.
