# Use imagem oficial com navegador e deps
FROM mcr.microsoft.com/playwright:v1.44.1-jammy

WORKDIR /app
ENV NPM_CONFIG_CACHE=/root/.npm

# Instalar dependências com cache
COPY package.json package-lock.json* ./
COPY .npmrc ./
RUN npm install --omit=dev
RUN npm rebuild esbuild --update-binary
RUN npm rebuild lightningcss --update-binary

# Copiar código restante e iniciar servidor dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
