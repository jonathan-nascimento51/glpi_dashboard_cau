"""Circuit breaker setup using pybreaker."""

from __future__ import annotations

from typing import Callable
import logging

import pybreaker
from prometheus_client import Gauge, Counter


breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)
state_gauge = Gauge("payment_circuit_state", "Circuit state", labelnames=["state"])
fail_counter = Counter("payment_failures", "Payment failures")


def call_with_breaker(func: Callable[..., None]) -> Callable[..., None]:
    def wrapper(*args, **kwargs):
        try:
            result = breaker.call(func, *args, **kwargs)
            state_gauge.labels(state=str(breaker.current_state)).set(1)
            return result
        except pybreaker.CircuitBreakerError:
            state_gauge.labels(state="open").set(1)
            raise
        except Exception:
            fail_counter.inc()
            raise

    return wrapper
