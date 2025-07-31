# Test Suite Overview

This directory contains unit and integration tests for the GLPI dashboard.

- `test_health_endpoint.py` verifies the `/v1/health` endpoint.
  - A `HEAD /v1/health` request should return `200` when GLPI is reachable.
  - When GLPI is unavailable (simulated via the `glpi_unavailable` fixture) the endpoint responds with `500`.
