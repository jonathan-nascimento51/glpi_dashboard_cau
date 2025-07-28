# Define o shell a ser usado e os comandos para ativar os ambientes.
# Isso garante que os comandos funcionem mesmo que o ambiente não esteja ativo no terminal do usuário.
SHELL := /bin/bash
VENV_ACTIVATE = source .venv/bin/activate &&
MISE_EXEC = mise exec --
FRONTEND_DIR = src/frontend/react_app

.PHONY: help setup dev dev-backend dev-frontend test test-backend test-frontend lint gen-types

help:
	@echo "Available commands:"
	@echo "  setup         - Set up the development environment from scratch."
	@echo "  dev           - Run backend and frontend development servers concurrently."
	@echo "  dev-backend   - Run the backend development server with auto-reload."
	@echo "  dev-frontend  - Run the frontend development server with auto-reload."
	@echo "  test          - Run all tests (backend and frontend)."
	@echo "  test-backend  - Run backend tests with pytest."
	@echo "  test-frontend - Run frontend tests with npm."
	@echo "  lint          - Run all linters and formatters with pre-commit."
	@echo "  gen-types     - Generate TypeScript types from Pydantic models."

setup: ## Set up the development environment
	sudo ./scripts/setup/setup_env.sh

dev: ## Run both backend and frontend servers
	@echo "Starting backend and frontend dev servers..."
	@make dev-backend & make dev-frontend

dev-backend: ## Run the backend development server
	@echo "🐍 Starting backend server on http://localhost:8000"
	$(VENV_ACTIVATE) uvicorn backend.api.worker_api:app --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## Run the frontend development server
	@echo "⚛️  Starting frontend server on http://localhost:5173"
	cd $(FRONTEND_DIR) && $(MISE_EXEC) npm run dev

test: ## Run all tests
	@make test-backend && make test-frontend

test-backend: ## Run backend tests
	@echo "🐍 Running backend tests..."
	$(VENV_ACTIVATE) pytest

test-frontend: ## Run frontend tests
	@echo "⚛️  Running frontend tests..."
	cd $(FRONTEND_DIR) && $(MISE_EXEC) npm test

lint: ## Run all linters
	@echo "Linting all files with pre-commit..."
	$(VENV_ACTIVATE) pre-commit run --all-files

gen-types: ## Generate TypeScript types from Pydantic models
	@echo "🔄 Generating TypeScript types from Pydantic models..."
	$(VENV_ACTIVATE) pydantic2ts --module shared.models.ts_models --output $(FRONTEND_DIR)/src/types/api.ts
