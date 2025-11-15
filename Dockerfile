# Stage 1: Build frontend (Preact) assets with Node
FROM node:20-bullseye-slim AS frontend-build

WORKDIR /app

# Copy only what's needed to install and build
COPY frontend/package*.json frontend/rollup.config.mjs frontend/tsconfig.json ./frontend/
COPY frontend/src ./frontend/src

# Ensure output directory exists and build
RUN mkdir -p static/dist \
    && cd frontend \
    && npm ci --no-audit --no-fund \
    && npm run build

# Stage 2: Python runtime image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy built frontend assets from the Node build stage
COPY --from=frontend-build /app/static/dist ./static/dist

# Run migrations inside CMD (runtime, not build time)
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 dart.asgi:application"]
