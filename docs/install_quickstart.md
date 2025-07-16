# Quick Installation Guide

This document condenses the main steps from the README to get the dashboard running.

## 1. Prepare the environment

1. Create the `.env` file from the template:
   ```bash
   python scripts/setup/setup_env.py
   ```
   Adjust the variables inside `.env` with your database and GLPI credentials.
   Docker Compose loads this file automatically when present.

2. Install dependencies and configure pre-commit:
   ```bash
   bash scripts/setup/setup_env.sh
   ```
   This command creates the `.venv` directory, installs packages from
   `requirements.txt` and `requirements-dev.txt`, and sets up `pre-commit`.
   Run it once before executing any tests (or use `make setup`). The script
   accepts proxy variables (`HTTP_PROXY`/`HTTPS_PROXY`) and can work offline with
   `OFFLINE_INSTALL=true` when wheels are available under `./wheels`.
   If proxies are disabled remember to clear them before running the setup:

   ```bash
   unset HTTP_PROXY HTTPS_PROXY
   ```
   Remove any leftover proxy entries from `.npmrc` as explained in
   [docs/solucoes_problemas.md](solucoes_problemas.md#11.1-unknown-env-config-http-proxy).
   If you prefer manual setup, execute:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```
   before running the tests.

3. (Optional) Authenticate the GitHub CLI if you use private repositories:
   ```bash
   export GITHUB_TOKEN=<token>
   bash scripts/setup/setup_github_access.sh
   ```

## 2. Run the services

Initialize the database, start the API and launch the dashboard:

```bash
PYTHONPATH=src python scripts/setup/init_db.py --drop-all
python worker.py &
python dashboard_app.py &
```

Alternatively use Docker to start all components:

```bash
docker compose up
```

## 3. Frontend development

Copy the React environment file, install Node packages and run Vite:

```bash
cp src/frontend/react_app/.env.example src/frontend/react_app/.env
cd src/frontend/react_app
npm install         # installs dotenv, @eslint/js and other dev dependencies
# npm ci can be used for reproducible installs
npm run dev
```
Docker Compose automatically loads `.env` when present.

For more details on proxy and offline installation see [docs/codex_setup.md](codex_setup.md).
