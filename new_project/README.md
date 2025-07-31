# New Project Scaffold

This folder contains a minimal setup for experiments separate from the main GLPI dashboard.

## Structure

- `backend/` – FastAPI worker exposing a `/health` endpoint.
  You can check the server status by visiting `/health`, which returns
  `{"status": "ok"}`.
- `frontend/` – placeholder React application (see `docs/frontend_architecture.md` for conventions).
- `shared/` – utilities shared between backend and frontend.

The directory includes basic Docker files to start the backend quickly.

## Environment

The Docker Compose file looks for a `.env` file in the project root using
`env_file: ../.env`. Copy `../.env.example` to `../.env` and fill in the
required settings before starting the containers.
