import pybreaker

from shared.resilience.circuit_breaker import breaker, call_with_breaker


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
