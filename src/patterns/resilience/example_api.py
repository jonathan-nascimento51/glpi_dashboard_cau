"""Example API call using retry_api_call."""

from __future__ import annotations

import random
import requests

from .retry_decorator import retry_api_call


@retry_api_call
def unstable_call(url: str) -> dict:
    if random.random() < 0.7:
        raise requests.exceptions.HTTPError("simulated failure")
    resp = requests.Response()
    resp._content = b'{"status": "ok"}'
    resp.status_code = 200
    return resp.json()


if __name__ == "__main__":
    print(unstable_call("http://example.com"))
