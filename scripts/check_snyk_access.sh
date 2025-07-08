#!/bin/bash
set -euo pipefail

# Simple connectivity check for snyk.io used in CI quality audits
URL="https://snyk.io"

# Try to reach snyk.io with a short timeout
if curl -Is "$URL" --max-time 10 >/dev/null 2>&1; then
  echo "✅ Connectivity to $URL confirmed"
  exit 0
else
  echo "❌ Unable to reach $URL. Check network permissions or proxy settings." >&2
  exit 1
fi
