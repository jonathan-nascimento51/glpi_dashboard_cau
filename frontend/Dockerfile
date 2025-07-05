FROM node:20-alpine

ENV NPM_CONFIG_CACHE=/root/.npm

# Instalação de dependências do sistema operacional
WORKDIR /app

COPY package.json package-lock.json* ./
# Use BuildKit cache to speed up dependency installation
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit --progress=false

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
