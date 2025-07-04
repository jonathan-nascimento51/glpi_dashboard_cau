#!/bin/bash
# Simple helper to set up the Python environment inside Codex or locally.
# It installs all dependencies, installs the package in editable mode and
# configures pre-commit hooks so that formatting and tests run automatically.

set -e

python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
pre-commit install
pip install testcontainers playwright      # opcional para testes e2e
npx playwright install                     # baixa o Chromium
pytest --cov=./
pre-commit autoupdate --all-files
pre-commit run --files requirements-dev.txt
