# New Project Scaffold

This folder contains a minimal setup for experiments separate from the main GLPI dashboard.

## Structure

- `backend/` – FastAPI worker exposing a `/health` endpoint.
- `frontend/` – placeholder React application (see `docs/frontend_architecture.md` for conventions).
- `shared/` – utilities shared between backend and frontend.

The directory includes basic Docker files to start the backend quickly.
