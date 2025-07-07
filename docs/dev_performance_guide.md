# Development Performance Guide

This document summarizes strategies to reduce the initial setup time when preparing a new development environment. The goal is to avoid the repeated cost of installing system packages and large dependencies every time a container is built from scratch.

## 1. Pre-built Base Image

Use the provided `Dockerfile` with the `INSTALL_PLAYWRIGHT` build argument set to `true` to produce a base image that already contains system dependencies, Python packages and Playwright browsers. Store this image in a registry accessible to the development team.

```bash
docker build --build-arg INSTALL_PLAYWRIGHT=true -t glpi-dashboard-base -f Dockerfile .
```

Publishing this base image allows subsequent `docker compose` runs to reuse the cached layers instead of repeating the installation process.

## 2. Cache Python Wheels

When network access is limited, download the project wheels once and reuse them:

```bash
./scripts/download_wheels.sh /tmp/wheels
```

Transfer the directory to the offline environment and install using:

```bash
pip install --no-index --find-links=/tmp/wheels -r requirements.txt -r requirements-dev.txt
```

## 3. Save Docker Images

The helper script `save_docker_images.sh` now accepts `--file` and `--output` arguments. Use it to export all images referenced by a compose file:

```bash
./scripts/save_docker_images.sh --file docker-compose.yml --output images.tar
```

Load the archive on an isolated machine with `docker load -i images.tar`.

## 4. Minimize `apt-get` Calls

Combine system package installations inside a single `RUN` layer within the Dockerfile. The current Dockerfile already consolidates packages to take advantage of build cache. Avoid repeating `apt-get update` in separate steps.

These practices help cut the environment setup time from minutes to seconds, especially when running in ephemeral CI/CD jobs or behind a corporate proxy.
