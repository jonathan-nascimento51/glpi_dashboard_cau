FROM python:3.12-slim

WORKDIR /app

# Install dependencies without a virtualenv
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.glpi_dashboard.services.worker_api:app", "--host", "0.0.0.0", "--port", "8000"]
