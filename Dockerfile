# Stage 1: Build frontend
FROM node:20-bullseye-slim AS frontend-build

WORKDIR /app
COPY frontend ./frontend

WORKDIR /app/frontend
RUN npm install
RUN npm run build   # creates /app/static because of outDir: '../../static/'

# Stage 2: Backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ Copy built static folder from build stage
COPY --from=frontend-build /app/static ./static

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 dart.asgi:application"]
