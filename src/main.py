from __future__ import annotations

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from glpi_dashboard.providers import AnalyticsService, create_container, setup

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)

container = create_container("https://glpi.example.com")
setup(container, app)

FastAPIInstrumentor().instrument_app(app)


@app.get("/dashboard")
async def get_dashboard(analytics: AnalyticsService) -> JSONResponse:
    return JSONResponse({"detail": "ok"})


if __name__ == "__main__":  # pragma: no cover - manual run
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000)
