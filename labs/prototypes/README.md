# Prototypes

The `labs/prototypes` folder collects experimental code. Each subdirectory is an isolated proof of concept not maintained as part of the main dashboard.

## fastapi_microservice

A minimal FastAPI setup used to test containerization and service orchestration. The project provides a `Dockerfile` and a `docker-compose.yml` that starts a small backend and a PostgreSQL instance.

**Status:** experimental, incomplete.

**Run locally**
```bash
cd labs/prototypes/fastapi_microservice
docker compose up --build
```

## monolith_clean_architecture

A toy project demonstrating a Clean Architecture layout. Only a few entities and application commands are implemented.

**Status:** proof of concept, unmaintained.

**Run**
There is no runnable entry point, but the folder can be explored or extended from `src/app`.
