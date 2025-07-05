"""OpenTelemetry metrics setup and helpers."""

from __future__ import annotations

import logging
import os
from typing import Optional

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

logger = logging.getLogger(__name__)

_unknown_enum_counter: Optional[metrics.Counter] = None
_api_failure_counter: Optional[metrics.Counter] = None
_api_latency_histogram: Optional[metrics.Histogram] = None
_ticket_process_histogram: Optional[metrics.Histogram] = None


def setup_telemetry() -> None:
    """Initialize MeterProvider and metric instruments."""
    if isinstance(metrics.get_meter_provider(), MeterProvider):
        return

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    raw_headers = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    headers = (
        {
            k: v
            for k, v in (
                item.split("=", 1)
                for item in raw_headers.split(",")
                if "=" in item
            )
        }
        if raw_headers
        else None
    )
    service_name = os.getenv("OTEL_SERVICE_NAME", "glpi_dashboard_cau")

    exporter = OTLPMetricExporter(endpoint=endpoint, headers=headers)
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(
        resource=Resource.create({ResourceAttributes.SERVICE_NAME: service_name}),
        metric_readers=[reader],
    )
    metrics.set_meter_provider(provider)
    meter = metrics.get_meter(__name__)

    global _unknown_enum_counter, _api_failure_counter
    global _api_latency_histogram, _ticket_process_histogram

    _unknown_enum_counter = meter.create_counter(
        "glpi_unknown_enum_total",
        description="Total number of unmapped enum values.",
    )
    _api_failure_counter = meter.create_counter(
        "glpi_api_failure_total",
        description="Total number of API failures.",
    )
    _api_latency_histogram = meter.create_histogram(
        "glpi_api_latency_seconds",
        unit="s",
        description="Latency of GLPI API requests.",
    )
    _ticket_process_histogram = meter.create_histogram(
        "glpi_ticket_process_seconds",
        unit="s",
        description="Duration to process tickets.",
    )
    logger.info("OpenTelemetry metrics initialized")


def record_unknown_enum(field_name: str) -> None:
    """Increment counter for unmapped enumeration fields."""
    if _unknown_enum_counter:
        _unknown_enum_counter.add(1, {"field_name": field_name})


def record_api_failure(reason: str) -> None:
    """Increment counter when API requests fail."""
    if _api_failure_counter:
        _api_failure_counter.add(1, {"reason": reason})


def record_api_latency(seconds: float, endpoint: str) -> None:
    """Record API latency in seconds."""
    if _api_latency_histogram:
        _api_latency_histogram.record(seconds, {"endpoint": endpoint})


def record_ticket_processing(seconds: float) -> None:
    """Record ticket processing duration."""
    if _ticket_process_histogram:
        _ticket_process_histogram.record(seconds)


__all__ = [
    "setup_telemetry",
    "record_unknown_enum",
    "record_api_failure",
    "record_api_latency",
    "record_ticket_processing",
]
