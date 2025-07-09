"""Retry decorator using Tenacity."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Callable

from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

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
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(fn)
