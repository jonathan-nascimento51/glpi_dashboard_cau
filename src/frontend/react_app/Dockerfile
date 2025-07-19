# 🔧 Node versão mínima exigida pelo Vite@7
FROM node:20.19.0-alpine
RUN apk add --no-cache bash curl

WORKDIR /app
ENV NPM_CONFIG_CACHE=/root/.npm

# Copiar apenas os arquivos de dependências primeiro para cache eficiente
COPY src/frontend/react_app/package.json src/frontend/react_app/package-lock.json* ./

# Instalar dependências, ignorando conflitos de peer dependencies que podem
# ocorrer com algumas versões de pacotes.
RUN npm install --legacy-peer-deps
# Copiar apenas o frontend
COPY src/frontend/react_app/ ./

# Copiar arquivo de env específico para Docker
COPY src/frontend/react_app/.env.docker .env

# Copiar script de healthcheck, se necessário
COPY scripts/healthchecks/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh
ENV HC_TARGET=frontend

# Expor a porta padrão do Vite
EXPOSE 5173

# Add Redis dependency check
RUN apk add --no-cache redis

HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=45s \
  --retries=3 \
  CMD ["bash", "/usr/local/bin/healthcheck.sh"]

CMD ["npm", "run", "dev"]
