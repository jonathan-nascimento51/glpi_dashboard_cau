#!/usr/bin/env bash
# Save all images referenced in docker-compose.yml for offline use
set -euo pipefail
OUTPUT=${1:-docker_images.tar}

# Pull images to ensure they exist locally
if ! docker compose pull; then
  echo "Failed to pull images" >&2
  exit 1
fi

# Extract image names from compose config
IMAGES=$(docker compose config | awk '/image:/ {print $2}')

docker save $IMAGES -o "$OUTPUT"
echo "Images saved to $OUTPUT"
