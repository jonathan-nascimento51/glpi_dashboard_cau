# Test Suite Overview

This directory contains unit and integration tests for the GLPI dashboard.

- `test_health_endpoint.py` verifies the `/health` endpoint.
  - A `HEAD /health` request returns `200` once the app reports it is ready.
  - Before readiness (`app.state.ready` is `False`) the endpoint responds with `503`.
