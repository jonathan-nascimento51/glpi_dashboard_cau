"""Entry point for running the simplified GLPI Dashboard API.

This module defines a standalone FastAPI application exposing only the
endpoints implemented in this exercise. It is intentionally minimal
compared to the fully fledged worker API present in the original
repository. The purpose of this file is to allow local execution and
testing of the new ``/api/tickets/summary-per-level`` endpoint without
pulling in the entire service stack.

Clients expecting to call the real worker API should use the
``backend/api/worker_api.py`` entrypoint instead.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.routes.tickets import router as tickets_router


def create_app() -> FastAPI:
    app = FastAPI(title="GLPI Dashboard Ticket Summary API")
    # Mount ticket summary routes without any prefix. The route itself
    # includes ``/api/tickets/summary-per-level``.
    app.include_router(tickets_router)
    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
