import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))  # noqa: E402

from glpi_dashboard import telemetry  # noqa: E402


def test_setup_and_record(monkeypatch):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    telemetry.setup_telemetry()
    telemetry.record_unknown_enum("status")
    telemetry.record_api_failure("timeout")
    telemetry.record_api_latency(0.5, "/tickets")
    telemetry.record_ticket_processing(1.2)
