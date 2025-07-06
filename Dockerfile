# =================================================================
# Estágio 1: Builder - Instala dependências e prepara a aplicação
# =================================================================
FROM python:3.12-slim AS builder

# Permite controlar instalação do Playwright via build-arg
ARG SKIP_PLAYWRIGHT=false

# 1. Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libx11-6 \
    libxshmfence1 \
    xvfb \
    fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

# Instalar Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

# 2. Criar ambiente virtual e ativar no PATH
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# 3. Copiar definições de dependências para cache
WORKDIR /app
COPY requirements.txt pyproject.toml setup.sh ./

# Instalar dependências Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 4. Instalar Playwright somente se não for dev
RUN if [ "$SKIP_PLAYWRIGHT" = "false" ]; then \
      pip install --no-cache-dir playwright && \
      playwright install chromium --with-deps; \
    fi

# 5. Copiar o restante do código
COPY . .

# =================================================================
# Estágio 2: Final - Imagem enxuta para produção
# =================================================================
FROM python:3.12-slim

# Instalar dependências mínimas de sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtualenv from builder
ENV VENV_PATH=/opt/venv
COPY --from=builder $VENV_PATH $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Copy application code and cached browsers (se houver)
COPY --from=builder /app /app
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health/glpi || exit 1

CMD ["python", "worker.py"]
