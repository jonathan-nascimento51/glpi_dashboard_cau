import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)  # noqa: E402

from opentelemetry.sdk.metrics.export import MetricExportResult

from backend.utils import telemetry  # noqa: E402


class DummyExporter:
    """Exporter that records metrics locally to avoid HTTP calls."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: D401
        """Ignore initialization parameters."""
        self.records = []
        self._preferred_temporality = {}
        self._preferred_aggregation = {}

    def export(self, batch, *args, **kwargs) -> MetricExportResult:  # noqa: D401
        """Store exported metrics in memory."""
        self.records.append(batch)
        return MetricExportResult.SUCCESS

    def force_flush(self, *args, **kwargs) -> MetricExportResult:
        return MetricExportResult.SUCCESS

    def shutdown(self, *args, **kwargs) -> None:  # noqa: D401
        """No-op shutdown."""
        self.records.clear()


def test_setup_and_record(monkeypatch):
    monkeypatch.setattr(telemetry, "OTLPMetricExporter", DummyExporter)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    telemetry.setup_telemetry()
    telemetry.record_unknown_enum("status")
    telemetry.record_api_failure("timeout")
    telemetry.record_api_latency(0.5, "/tickets")
    telemetry.record_ticket_processing(1.2)
