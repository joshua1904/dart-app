# Stage 1: Build frontend (Preact) assets with Node
FROM node:20-bullseye-slim AS frontend-build

WORKDIR /app

ENV NPM_CONFIG_REGISTRY=https://registry.npmjs.org/

COPY frontend/package*.json frontend/rollup.config.mjs frontend/tsconfig.json ./frontend/
COPY frontend/src ./frontend/src

WORKDIR /app/frontend

RUN npm install
RUN npm run build

WORKDIR /app

# Stage 2: Python runtime image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=frontend-build /app/static/dist ./static/dist

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 dart.asgi:application"]