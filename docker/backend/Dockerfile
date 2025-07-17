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

# Adiciona curl e o script de healthcheck
RUN apt-get update && apt-get install -y curl bash
COPY scripts/healthchecks/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

EXPOSE 8000
HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=60s \
  --retries=3 \
  CMD ["bash", "/usr/local/bin/healthcheck.sh"]

CMD ["python", "worker.py"]
