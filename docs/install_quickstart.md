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
  `requirements.txt` and the dev dependencies defined in `pyproject.toml`
  (compiled into `requirements-dev.txt`), and sets up `pre-commit`.
  Run it once before executing any tests (or use `make setup`). The script
  accepts proxy variables (`HTTP_PROXY`/`HTTPS_PROXY`). When a `wheels/`
  directory is present you can install completely offline by passing
  `OFFLINE_INSTALL=true`:

  ```bash
  bash scripts/setup/setup_env.sh OFFLINE_INSTALL=true
  ```

  Use `python scripts/download_wheels.py` on a machine with internet access to
  prefetch the required wheels. Set `INSECURE_TLS=true` to disable TLS
  verification when downloading Playwright (avoids certificate errors behind
  corporate proxies).
   If proxies are disabled remember to clear them before running the setup:

   ```bash
   unset HTTP_PROXY HTTPS_PROXY
   ```

   Remove any leftover proxy entries from `.npmrc` as explained in
   [docs/solucoes_problemas.md](solucoes_problemas.md#11.1-unknown-env-config-http-proxy).
   If you prefer manual setup, execute:

  ```bash
  pip install -r requirements.txt -r requirements-dev.txt  # generated via pip-compile
  # includes dev tools like pytest-cov used by coverage checks
  ```

   before running the tests.

1. (Optional) Authenticate the GitHub CLI if you use private repositories:

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
# optional but recommended with mise to avoid the .nvmrc warning
mise settings add idiomatic_version_file_enable_tools node
nvm install  # installs the version pinned in the repository's .nvmrc
nvm use
npm install         # installs dotenv, @eslint/js and other dev dependencies
# dotenv is required for environment variables loaded during tests
# npm ci can be used for reproducible installs
npm run dev
npm run storybook   # optional: preview UI components locally
```

The exact Node version is pinned in `.nvmrc` at the repository root.
Docker Compose automatically loads `.env` when present.
Docker can be used if you cannot install the required Node version.

For more details on proxy and offline installation see [docs/codex_setup.md](codex_setup.md).
