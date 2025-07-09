# Codex Environment Setup

This guide tracks adjustments required when running the project inside the Codex environment. Installations may fail if network access is limited or packages change over time. Use these steps to keep the environment operational.

## 1. Install dependencies

Run the helper script which installs both runtime and development requirements and activates pre-commit hooks:

```bash
./setup.sh
```

The script accepts optional variables:

- `HTTP_PROXY` / `HTTPS_PROXY` – configure outbound proxies.
- `OFFLINE_INSTALL=true` – install from the `./wheels` directory instead of contacting PyPI.
- `SKIP_PLAYWRIGHT=true` – skip the heavy browser download.

## 2. Update packages over time

When tests fail due to missing libraries, update `requirements.txt` and `requirements-dev.txt` accordingly, then regenerate the wheels if you maintain an offline cache:

```bash
./scripts/download_wheels.sh
```

After adjusting the lists rerun `./setup.sh` to refresh the virtual environment.

## 3. Troubleshooting

- Use `make test` to verify the installation. If imports fail, ensure that `pip install -r requirements-dev.txt` completed successfully.
- Review `/tmp/pytest.log` for failing modules and add the missing packages to the requirements files.

This document will evolve as new limitations are discovered.
