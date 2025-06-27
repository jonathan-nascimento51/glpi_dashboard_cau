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
pre-commit install  # optional
```

## 3. Configure environment variables

Generate the `.env` file then edit it with your values:

```bash
python scripts/setup_env.py
# then open .env and set tokens and database credentials
```

## 4. Prepare the data

Optionally download a JSON dump from GLPI:

```bash
python scripts/fetch_tickets.py --output tickets_dump.json
```

## 5. Start the Dash server

### Linux / macOS
```bash
python main.py
```

### Windows (CMD)
```bat
python main.py
```

### Windows (PowerShell)
```powershell
python main.py
```

The application will start at <http://127.0.0.1:8050>. Check the logs for any
connection errors when running in online mode.
