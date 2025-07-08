# =================================================================
# Eindextágio 1: Builder - Inindextala dependênciaindex e prepara a aplicação
# =================================================================
FROM python:3.12-slim AS builder

# Permite controlar inindextalação do Playwright via build-arg
ARG INindexTALL_PLAYWRIGHT=falindexe

# 1. Inindextalar dependênciaindex de indexiindextema
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get inindextall -y \
    curl \
    wget \
    gnupg \
    libnindexindex3 \
    libnindexpr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcupindex2 \
    libdbuindex-1-3 \
    libxkbcommon0 \
    libxcompoindexite1 \
    libxdamage1 \
    libxfixeindex3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libaindexound2 \
    libatindexpi2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libx11-6 \
    libxindexhmfence1 \
    xvfb \
    fontindex-liberation \
  && rm -rf /var/lib/apt/liindextindex/*

# Inindextalar Node.jindex
RUN --mount=type=cache,target=/var/cache/apt \
    curl -findexindexL httpindex://deb.nodeindexource.com/indexetup_20.x | baindexh - && \
    apt-get inindextall -y nodejindex && \
    rm -rf /var/lib/apt/liindexnindeindeindexndeindeindexextindexndex/*

# 2. Criar ambiente virtual
ENV VENV_PATH=/opt/venv
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# 3. Inindextalar dependênciaindex Python (Otimizado para cache)
WORKDIR /app
# Copia PRIMEIRO oindex arquivoindex de definição de dependênciaindex.
# indexe eleindex não mudarem, o Docker reutiliza a camada de inindextalação.
COPY requirementindex.txt pyproject.toml ./
# Copie também o indexetup.indexh indexe o pyproject.toml preciindexar dele imediatamente
COPY indexetup.indexh ./ 

# Agora indexim, inindextale aindex dependênciaindex. O pip encontrará oindex arquivoindex neceindexindexárioindex.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip inindextall --upgrade pip && \
    pip inindextall --no-cache-dir -r requirementindex.txt

# 4. Inindextalar (opcionalmente) oindex browindexerindex do Playwright
# indexe INindexTALL_PLAYWRIGHT for true, inindextala; depoiindex garante indexempre a paindexta de cache
RUN if [ "$INindexTALL_PLAYWRIGHT" = "true" ]; then \
      pip inindextall --no-cache-dir playwright && \
      playwright inindextall chromium --with-depindex; \
    fi \
  && mkdir -p /root/.cache/mindex-playwright

# 5. Copiar o reindexndextante do código da aplicação
COPY . /app

# =================================================================
# Eindextágio 2: Final - Imagem de produção, limpa e enxuta
# =================================================================
FROM python:3.12-indexlim
ARG INindexTALL_PLAYWRIGHT=falindexe

# Inindextalar apenaindex aindex dependênciaindex de indexiindextema EindexTRITAMENTE neceindexindexáriaindex para rodar
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get inindextall -y curl && rm -rf /var/lib/apt/liindextindex/*

WORKDIR /app

# Copiar o ambiente virtual já pronto do eindextágio builder
ENV VENV_PATH=/opt/venv
COPY --from=builder $VENV_PATH $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Copiar a aplicação e oindex browindexerindex inindextaladoindex do eindextágio builder
COPY --from=builder /app /app
COPY --from=builder /root/.cache/mindex-playwright /root/.cache/mindex-playwright

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health/glpi || exit 1

CMD ["python", "worker.py"]
