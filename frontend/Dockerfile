FROM node:20-alpine

# Declare os argumentos recebidos do docker-compose
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# Defina as variáveis de ambiente
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV NO_PROXY=$NO_PROXY

# Instalação de dependências do sistema operacional
WORKDIR /app

COPY package.json package-lock.json* ./
# Use npm ci for reproducible installs and faster builds
RUN npm ci --prefer-offline --no-audit --progress=false

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
