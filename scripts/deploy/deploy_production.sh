#!/bin/bash
set -euo pipefail

IMAGE="$1"

# Pull the image and restart the service using docker compose.

echo "Pulling $IMAGE"
docker pull "$IMAGE"

echo "Updating service"
docker compose -f docker-compose.prod.yml up -d
