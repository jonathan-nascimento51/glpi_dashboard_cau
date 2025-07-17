# Docker Compose Adjustments

This file documents path corrections applied to docker-compose files.

## tests/integration/docker-compose.yml
- Added `dockerfile: docker/backend/Dockerfile` to the `api-server` service to ensure the correct Dockerfile is used when building from the repository root.
