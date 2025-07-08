FROM python:3.12-slim

WORKDIR /app

# ---------------------------
# 1. Copie apenas os manifestos
# ---------------------------
COPY requirements.txt pyproject.toml ./

# ---------------------------------------------------
# 2. Instale dependências usando cache do pip (mais rápido)
# ---------------------------------------------------
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------
# 3. Copie o restante do código e instale em modo editável
# ---------------------------------------------------
COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8000

HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=10s \
  --retries=3 \
  CMD curl -f http://localhost:8000/health/glpi || exit 1
CMD ["python", "worker.py"]
