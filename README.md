# ==========================
# Stage 1: build frontend
# ==========================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ==========================
# Stage 2: backend (Django + Daphne)
# ==========================
FROM python:3.12-slim AS backend

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=dart.settings \
    PORT=8000

# Create app directory
WORKDIR /app

# Install system deps (for psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY dart/ ./dart/
COPY main/ ./main/
COPY manage.py ./
COPY .env.example .env

# Copy frontend build output (if any)
COPY --from=frontend-builder /app/frontend/dist ./main/static/frontend/

# Create database folder
RUN mkdir -p db

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Entrypoint: run migrations + start Daphne
CMD python manage.py migrate && \
    daphne -b 0.0.0.0 -p ${PORT} dart.asgi:application
