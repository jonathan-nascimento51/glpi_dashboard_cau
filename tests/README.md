# Test Suite Overview

This directory contains unit and integration tests for the GLPI dashboard.

- `test_health_endpoint.py` verifies the `/health` endpoint. This route only
  signals API readiness and does **not** guarantee connectivity with the GLPI
  server.
  - A `HEAD /health` request returns `200` once the app reports it is ready.
  - Before readiness (`app.state.ready` is `False`) the endpoint responds with
    `503`.
  - Monitor the actual GLPI connection through metrics or a dedicated check.
