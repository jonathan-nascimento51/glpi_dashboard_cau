"""Retry decorator using Tenacity."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Callable

from tenacity import (
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
)

logger = logging.getLogger(__name__)


def _json_log(retry_state):
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "attempt": retry_state.attempt_number,
        "exception": (
            str(retry_state.outcome.exception()) if retry_state.outcome else None
        ),
    }
    logger.warning(json.dumps(data))


def retry_api_call(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Retry decorator with optional backoff disabling for tests."""

    if os.environ.get("DISABLE_RETRY_BACKOFF"):
        wait_strategy = wait_fixed(0)
    else:
        wait_strategy = wait_exponential(multiplier=1, min=1, max=10)

    return retry(
        stop=stop_after_attempt(5),
        wait=wait_strategy,
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(fn)
