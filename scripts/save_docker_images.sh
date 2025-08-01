#!/usr/bin/env bash
# Save Docker images referenced in a compose file for offline use.
# Usage: ./save_docker_images.sh [--file <compose.yml>] [--output <tar>]
# Run with -h or --help to display this message.
set -euo pipefail

COMPOSE_FILE="docker-compose.yml"
OUTPUT="docker_images.tar"

usage() {
  echo "Usage: $0 [--file <compose.yml>] [--output <tar>]" >&2
  echo "Default compose file is docker-compose.yml; output defaults to docker_images.tar" >&2
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--file)
      COMPOSE_FILE="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage 1
      ;;
  esac
done

# Verify compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Compose file '$COMPOSE_FILE' not found" >&2
  exit 1
fi

# Pull images to ensure they exist locally
if ! docker compose -f "$COMPOSE_FILE" pull; then
  echo "failed to pull images" >&2
  exit 1
fi

# Extract image names from compose config
readarray -t IMAGES < <(docker compose -f "$COMPOSE_FILE" config | awk '/image:/ {print $2}' | sort -u)

# Save images to tar archive
docker save "${IMAGES[@]}" -o "$OUTPUT"
echo "Images saved to $OUTPUT"
