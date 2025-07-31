FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
