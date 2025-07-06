# =================================================================
# Estágio 1: Builder - Instala dependências e prepara a aplicação
# =================================================================
FROM python:3.12-slim AS builder

# Permite controlar instalação do Playwright via build-arg
ARG INSTALL_PLAYWRIGHT=false

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
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs

# 2. Criar ambiente virtual
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# 3. Instalar dependências Python (Otimizado para cache)
WORKDIR /app
# Copia PRIMEIRO os arquivos de definição de dependências.
# Se eles não mudarem, o Docker reutiliza a camada de instalação.
COPY requirements.txt pyproject.toml ./
# Copie também o setup.sh se o pyproject.toml precisar dele imediatamente
COPY setup.sh ./ 

# Agora sim, instale as dependências. O pip encontrará os arquivos necessários.
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar o restante do código da aplicação
COPY . .

# 5. Instalar (opcionalmente) os browsers do Playwright
# A instalação pode ser custosa; permite-se desativar via argumento de build
RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then \
      pip install --no-cache-dir playwright && \
      playwright install chromium --with-deps; \
    else \
      mkdir -p /root/.cache/ms-playwright; \
    fi

# =================================================================
# Estágio 2: Final - Imagem de produção, limpa e enxuta
# =================================================================
FROM python:3.12-slim
ARG INSTALL_PLAYWRIGHT=false

# Instalar apenas as dependências de sistema ESTRITAMENTE necessárias para rodar
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar o ambiente virtual já pronto do estágio builder
ENV VENV_PATH=/opt/venv
COPY --from=builder $VENV_PATH $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Copiar a aplicação e os browsers instalados do estágio builder
COPY --from=builder /app /app
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health/glpi || exit 1

CMD ["python", "worker.py"]