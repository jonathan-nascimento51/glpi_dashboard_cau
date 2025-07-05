from __future__ import annotations

import logging

import httpx
from dishka import Provider, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from opentelemetry.sdk.metrics import MeterProvider
from purgatory import AsyncCircuitBreakerFactory

from .glpi_client import GLPIApiClient


class AnalyticsService:
    """Placeholder analytics service."""


class GlpiProvider(Provider):
    """Dishka provider wiring GLPI-related dependencies."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient()
        self._breaker_factory = AsyncCircuitBreakerFactory()

        self.provide(self._get_client, scope=Scope.APP)
        self.provide(self._get_breaker_factory, scope=Scope.APP)
        self.provide(self._get_api_client, scope=Scope.REQUEST)
        self.provide(self._get_analytics, scope=Scope.REQUEST)
        self.provide(self._get_meter_provider, scope=Scope.REQUEST)
        self.provide(self._get_logger, scope=Scope.REQUEST)

    # APP scoped ---------------------------------------------------------
    def _get_client(self) -> httpx.AsyncClient:
        return self._client

    def _get_breaker_factory(self) -> AsyncCircuitBreakerFactory:
        return self._breaker_factory

    # REQUEST scoped -----------------------------------------------------
    def _get_api_client(self) -> GLPIApiClient:
        return GLPIApiClient(self._base_url, self._client)

    def _get_analytics(self) -> AnalyticsService:
        return AnalyticsService()

    def _get_meter_provider(self) -> MeterProvider:
        return MeterProvider()

    def _get_logger(self) -> logging.Logger:
        return logging.getLogger("glpi")


def create_container(base_url: str):
    provider = GlpiProvider(base_url)
    return make_async_container(provider)


def setup(container, app: FastAPI) -> None:
    """Attach Dishka container to FastAPI app."""
    setup_dishka(container, app)
