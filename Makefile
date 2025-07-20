# Makefile

VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

setup:
	bash scripts/setup/setup_env.sh

diagnose:
	bash scripts/diagnostics/run_codex_diagnose.sh

refactor-init:
	bash scripts/refactor/init_refactor.sh

build:
	docker compose build

up:
	docker compose up

reset:
	docker compose down -v && docker compose up --build

logs:
	docker compose logs -f

down:
	docker compose down

init-db: | $(PYTHON)
	$(PYTHON) scripts/setup/init_db.py

# Running `make test` will bootstrap the virtualenv if `.venv/bin/pip` is missing
test: | $(PIP)
	$(PIP) install --break-system-packages -r requirements.txt -r requirements-dev.txt
	$(PIP) install -e .
	PYTHONPATH=src $(VENV)/bin/pytest

$(PIP):
	$(MAKE) setup

lint:
	flake8 .
	black --check .
	isort --check-only .
	ruff check .

format:
	black .
	isort .
	ruff check --fix .

bug-prompt:
	$(PYTHON) scripts/generate_bug_prompt.py --output bug_prompt.md

gen-types:
       PYTHONPATH=src pydantic2ts --module backend.models.ts_models --output src/frontend/react_app/src/types/api.ts

lint-config:
	bash scripts/lint-configs.sh

lint-docker:
	bash scripts/lint-docker.sh

.PHONY: setup build up reset logs down init-db test lint format bug-prompt gen-types lint-config lint-docker
