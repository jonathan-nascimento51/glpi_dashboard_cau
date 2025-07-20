import pytest

pytest.importorskip("pybreaker")
import pybreaker

from shared.utils.resilience import breaker, call_with_breaker


def failing():
    raise RuntimeError


wrapped = call_with_breaker(failing)


def test_breaker_opens_after_failures():
    for _ in range(5):
        try:
            wrapped()
        except (RuntimeError, pybreaker.CircuitBreakerError):
            pass
    assert breaker.current_state == pybreaker.STATE_OPEN


class DummyGauge:
    def __init__(self):
        self.calls = []

    def labels(self, *, state):
        class L:
            def __init__(self, outer):
                self.outer = outer

            def set(self, value):
                self.outer.calls.append((state, value))

        return L(self)


class DummyCounter:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1


def test_call_with_breaker_records_metrics(monkeypatch):
    breaker.close()
    gauge = DummyGauge()
    counter = DummyCounter()
    monkeypatch.setattr("shared.utils.resilience.circuit_breaker.state_gauge", gauge)
    monkeypatch.setattr("shared.utils.resilience.circuit_breaker.fail_counter", counter)

    @call_with_breaker
    def ok():
        return "ok"

    result = ok()
    assert result == "ok"
    assert gauge.calls[-1] == (str(breaker.current_state), 1)
    assert counter.count == 0

    @call_with_breaker
    def bad():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        bad()
    assert counter.count == 1


def test_call_with_breaker_open_state(monkeypatch):
    gauge = DummyGauge()
    counter = DummyCounter()
    monkeypatch.setattr("shared.utils.resilience.circuit_breaker.state_gauge", gauge)
    monkeypatch.setattr("shared.utils.resilience.circuit_breaker.fail_counter", counter)
    breaker.open()

    @call_with_breaker
    def ok():
        return "x"

    with pytest.raises(pybreaker.CircuitBreakerError):
        ok()
    assert ("open", 1) in gauge.calls
    assert counter.count == 0
    breaker.close()
