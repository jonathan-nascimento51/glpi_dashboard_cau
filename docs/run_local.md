# Running the Dashboard Locally

This guide details how to configure a virtual environment, install dependencies and start the Dash server on **Linux** and **Windows**.

## 1. Create and activate a virtual environment

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (CMD)

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install the dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .  # install package locally (packages live under src/)
pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
pre-commit install  # optional
```

## 3. Configure environment variables

Generate the `.env` file then edit it with your values:

```bash
python scripts/setup/setup_env.py
# then open .env and set tokens and database credentials
```

## 4. Validar credenciais GLPI

Execute o script abaixo para confirmar que suas credenciais estão corretas:

```bash
python scripts/validate_credentials.py
```

If HTTP_PROXY or HTTPS_PROXY is defined in your shell, the checker will
automatically use those values when connecting to GLPI.

Saída esperada em caso de sucesso:

```text
✅ Conexão com GLPI bem-sucedida!
```

Se ocorrer algum erro, ajuste o arquivo `.env` antes de prosseguir com `docker compose up`.
Certifique-se de que o plugin Docker Compose (v2) esteja instalado. Caso o comando
`docker compose` não seja reconhecido, instale o pacote `docker-compose-plugin` ou
atualize o Docker Engine.

## 5. Prepare the data

Optionally generate a JSON dump from GLPI. A small sanitized sample is already
available in `resources/data/raw_tickets_sample.json`:

```bash
python scripts/fetch/fetch_tickets.py --output data/tickets_dump.json
```

## 6. Start the Dash server

### 6.1 Linux / macOS

```bash
python dashboard_app.py
```

### 6.2 Windows (CMD)

```bat
python dashboard_app.py
```

### 6.3 Windows (PowerShell)

```powershell
python dashboard_app.py
```

The application will start at <http://127.0.0.1:8050>. Check the logs for any
connection errors when running in online mode.

## Offline Docker images

If the host has no internet access, you can preload all Docker images used by
`docker-compose.yml` on a machine that does. Run the helper script and transfer
the tarball to the offline environment:

```bash
./scripts/save_docker_images.sh --file docker-compose.yml --output images.tar
docker load -i images.tar
```

Start the stack normally with `docker compose up` after loading the archive.

## Temporary build directory

When running packaging commands such as `python -m build` or `npm run build`, artifacts are placed in the `build/` folder. This directory is only meant for transient files and is listed in `.gitignore`.
