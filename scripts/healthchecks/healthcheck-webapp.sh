#!/usr/bin/env bash
# Healthcheck script for the FastAPI web application.
# Performs an HTTP request to the health endpoint.
set -euo pipefail

WEBAPP_URL="${WEBAPP_URL:-http://localhost:8000/health}"

curl --fail --head "$WEBAPP_URL" > /dev/null
