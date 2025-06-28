.PHONY: init-db test

init-db:
	python scripts/init_db.py

test:
	pip install -r requirements.txt -r requirements-dev.txt
	pytest --cov=./
