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
# then open .env and set tokens, database credentials and USE_MOCK
```

If you plan to use the offline mode, ensure `USE_MOCK=true` and that the
`KNOWLEDGE_BASE_FILE` path points to a valid JSON file. To fetch real data from
GLPI, set `USE_MOCK=false` and provide your API tokens.

## 4. Prepare the data

### Offline
```bash
python scripts/gen_mock_data.py --count 100 --null-rate 0.1
```

### Online
```bash
python scripts/fetch_tickets.py --output mock/sample_data.json
```

## 5. Start the Dash server

### Linux / macOS
```bash
python main.py                        # uses mock data
USE_MOCK=false python main.py         # fetch from API
```

### Windows (CMD)
```bat
python main.py                        & rem uses mock data
set USE_MOCK=false && python main.py  & rem fetch from API
```

### Windows (PowerShell)
```powershell
python main.py                        # uses mock data
$env:USE_MOCK="false"; python main.py  # fetch from API
```

The application will start at <http://127.0.0.1:8050>. Check the logs for any
connection errors when running in online mode.
