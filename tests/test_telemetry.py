import os
import sys


from opentelemetry.sdk.metrics.export import MetricExportResult

from shared.utils import telemetry  # noqa: E402


sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)


class DummyExporter:
    """Exporter that records metrics locally to avoid HTTP calls."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: D401
        self.records: list[list] = []
        self._preferred_temporality: dict[str, str] = {}
        self._preferred_aggregation: dict[str, str] = {}

    def export(self, batch, timeout_millis=10000, **kwargs) -> MetricExportResult:
        self.records.append(batch)
        return MetricExportResult.SUCCESS

    def force_flush(self, timeout_millis=10000):
        return True

    def shutdown(self, timeout_millis=30000, **kwargs) -> None:
        self.records.clear()


def test_setup_and_record(monkeypatch):
    monkeypatch.setattr(telemetry, "OTLPMetricExporter", DummyExporter)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    telemetry.setup_telemetry()
    telemetry.record_unknown_enum("status")
    telemetry.record_api_failure("timeout")
    telemetry.record_api_latency(0.5, "/tickets")
    telemetry.record_ticket_processing(1.2)


def test_metric_export(monkeypatch):
    exporter = DummyExporter()
    monkeypatch.setattr(telemetry, "OTLPMetricExporter", lambda *a, **k: exporter)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    telemetry.setup_telemetry()
    telemetry.record_unknown_enum("status")
    telemetry.record_api_failure("timeout")
    telemetry.record_api_latency(0.1, "/tickets")
    telemetry.record_ticket_processing(0.2)

    provider = telemetry.metrics.get_meter_provider()
    provider.force_flush()
    assert exporter.records
    from typing import Any, cast

    data = cast(Any, exporter.records[0])
    names = [
        m.name
        for rm in data.resource_metrics
        for sm in rm.scope_metrics
        for m in sm.metrics
    ]
    assert {
        "glpi_unknown_enum_total",
        "glpi_api_failure_total",
        "glpi_api_latency_seconds",
        "glpi_ticket_process_seconds",
    }.issubset(names)
    provider.shutdown()
    telemetry.metrics.set_meter_provider(telemetry.metrics.NoOpMeterProvider())
