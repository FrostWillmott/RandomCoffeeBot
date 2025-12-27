# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Random Coffee Bot - a FastAPI-based bot for organizing random coffee meetings. Uses aiogram for Telegram bot integration.

## Tech Stack

- Python 3.13+
- FastAPI (web framework)
- SQLAlchemy + asyncpg (async database)
- Celery + Redis (task queue)
- aiogram (Telegram bot framework)
- Docker + Docker Compose
- Traefik (reverse proxy)
- uv (package manager)

## Project Structure

```
app/                    # Main application package
├── main.py            # FastAPI application entry point
├── config.py          # Pydantic Settings configuration
├── api/v1/            # API endpoints (versioned)
├── db/                # Database layer (SQLAlchemy)
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── services/          # Business logic
└── workers/           # Celery tasks
    └── celery_app.py  # Celery configuration
```

## Development Commands

### Docker (recommended)

```bash
# Start development environment
make dev

# Build and start
make dev-build

# View logs
make logs

# Open shell in container
make shell

# Stop containers
make down
```

### Database

```bash
# Run migrations
make migrate

# Create new migration
make makemigration MSG="add users table"
```

### Without Docker

```bash
# Install dependencies
uv sync --all-extras --dev

# Run the application
uvicorn app.main:app --reload

# Linting and formatting
ruff check .
ruff format .

# Type checking
mypy .
```

## Docker Services

Development (`docker-compose.yml`):
- `app` - FastAPI (port 8000)
- `db` - PostgreSQL 16 (port 5432)
- `redis` - Redis 7 (port 6379)
- `celery-worker` - Celery worker
- `celery-beat` - Celery scheduler
- `flower` - Celery monitoring (port 5555)
- `mailhog` - Dev SMTP (ports 1025, 8025)
- `traefik` - Reverse proxy (ports 80, 8080)

Production (`docker-compose.prod.yml`):
- Same services with TLS, resource limits, healthchecks

## Code Style

- Line length: 79 characters
- Indent: 4 spaces
- Quote style: double quotes
- Docstrings: Google convention
- Ruff rules: E, W, F, D, C901, I, N, UP, Q, RUF, B, ISC

## API Endpoints

- `GET /` - Root greeting
- `GET /hello/{name}` - Parameterized greeting
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/ready` - Readiness check (with DB)

API docs: `/docs` (Swagger), `/redoc`
