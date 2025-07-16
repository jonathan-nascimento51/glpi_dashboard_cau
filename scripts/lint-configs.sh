#!/usr/bin/env bash
set -e

echo "🔍 Checking frontend Dockerfile Node version…"
grep -q "node:20" frontend/Dockerfile || {
  echo "ERROR: frontend/Dockerfile not using Node 20+"
  exit 1
}

echo "🔍 Checking API_BASE_URL…"
grep -q "backend:8000" .env || {
  echo "ERROR: NEXT_PUBLIC_API_BASE_URL must be http://backend:8000"
  exit 1
}

echo "🔍 Checking Redis sysctl…"
grep -q "vm.overcommit_memory=1" docker-compose.yml || {
  echo "ERROR: Redis sysctl missing"
  exit 1
}

echo "✅ All config checks passed!"
