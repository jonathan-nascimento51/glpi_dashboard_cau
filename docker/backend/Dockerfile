FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt requirements-dev.txt pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Adiciona curl para healthcheck funcional
RUN apt-get update && apt-get install -y curl

EXPOSE 8000
HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=10s \
  --retries=3 \
  CMD curl -f http://localhost:8000/health/glpi || exit 1

CMD ["python", "worker.py"]
