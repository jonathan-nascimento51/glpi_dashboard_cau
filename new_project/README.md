# New Project Scaffold

This folder contains a minimal setup for experiments separate from the main GLPI dashboard.

## Structure

- `backend/` – FastAPI worker exposing a `/health` endpoint.
  You can check the server status by visiting `/health`, which returns
  `{"status": "ok"}`.
- `frontend/` – placeholder React application (see `docs/frontend_architecture.md` for conventions).
- `shared/` – utilities shared between backend and frontend.

The directory includes basic Docker files to start the backend quickly.

## Quick Start

Follow these steps to spin up the experimental stack locally:

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

   Fill in your `GLPI_BASE_URL`, `GLPI_APP_TOKEN` and either
   `GLPI_USER_TOKEN` or `GLPI_USERNAME`/`GLPI_PASSWORD` in the newly
   created `.env` file.

2. Build and start the containers:

   ```bash
   docker compose -f new_project/docker-compose.yml up --build
   ```

   The API will be available on <http://localhost:8000>. You should be
   able to reach:

   - <http://localhost:8000/health>
   - <http://localhost:8000/tickets>
   - <http://localhost:8000/metrics>

3. Run the test suite to verify everything is wired correctly:

   ```bash
   pytest new_project/tests
   ```

All endpoints above return JSON responses when the stack is running.
