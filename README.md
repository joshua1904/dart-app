## Dart App — Developer Guide

A Django 5 + Channels 4 project served via ASGI (Daphne). This guide covers local setup, common commands, and Docker.

### Requirements
- Python 3.12
- pip
- (Optional) Docker and Docker Compose

### Quick start (local)
```bash
# From the repo root
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

mkdir db
python manage.py migrate
DJANGO_SUPERUSER_PASSWORD='root' python manage.py createsuperuser --username='root' --email='admin@example.com' --noinput

cp .env.example .env
# Start the dev server (ASGI-aware runserver via Channels)
python manage.py runserver 0.0.0.0:8000
```
App will be available at `http://localhost:8000`.

### Running tests
```bash
python manage.py test
```

### Formatting
```bash
# Auto-format
black .
```

### Static files
In development, static files are served automatically. For production builds you will need:
```bash
python manage.py collectstatic --noinput
```

### Docker
Build and run using Docker:
```bash
docker compose up --build
# then visit http://localhost:8000
```
The container entrypoint runs migrations and serves via Daphne.

### Project layout (high-level)
- `dart/`: Django project settings and ASGI config
- `main/`: Application code (models, views, consumers, templates, static)
  - `consumers/`: WebSocket consumers (Channels)
  - `business_logic/`: Game and statistics logic
  - `templates/` and `static/`: UI and assets
- `db/`: SQLite database location (default for dev)