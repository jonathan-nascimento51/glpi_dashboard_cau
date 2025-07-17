# 🔧 Node versão mínima exigida pelo Vite@7
FROM node:20.19.0-alpine

WORKDIR /app
ENV NPM_CONFIG_CACHE=/root/.npm

# Copiar apenas os arquivos de dependências primeiro para cache eficiente
COPY src/frontend/react_app/package.json src/frontend/react_app/package-lock.json* ./

# Instalar dependências sem conflito de peer dependencies
RUN PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --legacy-peer-deps
RUN npm rebuild esbuild --update-binary
RUN npm rebuild lightningcss --update-binary

# Copiar apenas o frontend
COPY src/frontend/react_app/ ./

# Copiar arquivo de env específico para Docker
COPY .env.docker .env

# Copiar script de healthcheck, se necessário
COPY scripts/healthchecks/healthcheck-webapp.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Expor a porta padrão do Vite
EXPOSE 5173

HEALTHCHECK \
  --interval=30s \
  --timeout=5s \
  --start-period=45s \
  --retries=3 \
  CMD /usr/local/bin/healthcheck.sh

CMD ["npm", "run", "dev"]
