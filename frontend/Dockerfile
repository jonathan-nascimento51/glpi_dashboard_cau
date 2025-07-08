FROM node:20-slim

RUN npm install -g npm@latest
ENV NPM_CONFIG_CACHE=/root/.npm

WORKDIR /app

# 1) Copia package.json + lockfile
COPY package.json package-lock.json* ./

# 2) Copia o .npmrc renomeado
COPY .npmrc ./

# 2) Usa npm install em vez de ci para garantir optionalDependencies
RUN --mount=type=cache,target=/root/.npm \
    npm install --omit=dev

# 4) Copia o restante do código e executa build/dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
