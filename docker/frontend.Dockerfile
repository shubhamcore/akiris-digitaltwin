FROM node:24-alpine

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
EXPOSE 5173

# API_UPSTREAM points at the backend service in compose
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
