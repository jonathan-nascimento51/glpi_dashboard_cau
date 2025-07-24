"""API routers for the dashboard service."""

from fastapi import APIRouter

router = APIRouter()

from . import metrics  # noqa: E402,F401

router.include_router(metrics.router)

__all__ = ["router"]
