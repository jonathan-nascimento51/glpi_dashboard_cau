# Makefile

setup:
	python -m venv .venv && source .venv/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt

build:
	docker-compose build

up:
	docker-compose up

reset:
	docker-compose down -v && docker-compose up --build

logs:
	docker-compose logs -f

down:
	docker-compose down

.PHONY: init-db test

init-db:
	python scripts/init_db.py

test:
	# install runtime and development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pip install -e .  # ensure local package is discoverable
	pytest --cov=./
