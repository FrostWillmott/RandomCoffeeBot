.PHONY: help install run dev dev-build down logs shell ps stats migrate makemigration db-reset db-seed db-shell prod prod-build prod-down prod-logs test test-watch test-coverage test-db-up test-db-down lint format typecheck pre-commit install-hooks ci clean prune

# Default target
help:
	@echo "RandomCoffeeBot Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies with uv"
	@echo "  make install-hooks - Install pre-commit hooks"
	@echo ""
	@echo "Local Development (no Docker):"
	@echo "  make run          - Run bot locally"
	@echo ""
	@echo "Docker Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make down         - Stop all containers"
	@echo "  make logs         - View container logs"
	@echo "  make shell        - Open shell in bot container"
	@echo "  make ps           - Show running containers"
	@echo "  make stats        - Show container resource usage"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make makemigration MSG='message' - Create new migration"
	@echo "  make db-reset     - Reset database (drop and recreate)"
	@echo "  make db-seed      - Seed database with topics"
	@echo "  make db-shell     - Open PostgreSQL shell"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production"
	@echo "  make prod-down    - Stop production containers"
	@echo "  make prod-logs    - View production logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run tests (auto-manages test DB)"
	@echo "  make test-watch   - Run tests in watch mode"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make test-db-up   - Start test database container"
	@echo "  make test-db-down - Stop test database container"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linter (ruff check)"
	@echo "  make format       - Format code (ruff format)"
	@echo "  make typecheck    - Run type checker (mypy)"
	@echo "  make pre-commit   - Run all pre-commit hooks"
	@echo "  make ci           - Run all CI checks locally"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove containers, volumes, images"
	@echo "  make prune        - Docker system prune"

# Setup
install:
	uv sync --all-extras

install-hooks:
	uv run pre-commit install

# Local Development
run:
	uv run python -m app.main

# Docker Development
dev:
	docker compose up -d

dev-build:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec bot bash

ps:
	docker compose ps

stats:
	docker stats --no-stream

# Database
migrate:
	docker compose exec bot alembic upgrade head

makemigration:
	docker compose exec bot alembic revision --autogenerate -m "$(MSG)"

db-reset:
	@echo "Resetting database..."
	docker compose down db
	docker volume rm randomcoffee-postgres-data || true
	docker compose up -d db
	@echo "Waiting for database to be ready..."
	@sleep 5
	docker compose exec bot alembic upgrade head
	@echo "Database reset complete"

db-seed:
	docker compose exec bot sh -c "PYTHONPATH=/app python scripts/seed_topics.py"

db-shell:
	@POSTGRES_USER=$$(docker compose exec -T db printenv POSTGRES_USER 2>/dev/null || echo "postgres"); \
	POSTGRES_DB=$$(docker compose exec -T db printenv POSTGRES_DB 2>/dev/null || echo "randomcoffee"); \
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

# Production
prod:
	docker compose -f docker-compose.prod.yml up -d

prod-build:
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

# Quality
test:
	@echo "Starting test database..."
	@docker compose -f docker-compose.test.yml up -d db-test
	@echo "Waiting for database to be ready..."
	@sleep 3
	@echo "Running tests..."
	@uv run pytest tests/ -v
	@echo "Stopping test database..."
	@docker compose -f docker-compose.test.yml down

test-watch:
	@echo "Starting test database..."
	@docker compose -f docker-compose.test.yml up -d db-test
	@sleep 3
	@uv run pytest tests/ -v --looponfail
	@docker compose -f docker-compose.test.yml down

test-coverage:
	@echo "Starting test database..."
	@docker compose -f docker-compose.test.yml up -d db-test
	@sleep 3
	@uv run pytest tests/ --cov=app --cov-report=html --cov-report=term
	@docker compose -f docker-compose.test.yml down

test-db-up:
	@docker compose -f docker-compose.test.yml up -d db-test
	@echo "Test database started on port 5433"

test-db-down:
	@docker compose -f docker-compose.test.yml down
	@echo "Test database stopped"

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy app

pre-commit:
	uv run pre-commit run --all-files

ci:
	@echo "Running all CI checks..."
	@echo "1. Linting..."
	@uv run ruff check .
	@echo "2. Formatting check..."
	@uv run ruff format --check .
	@echo "3. Type checking..."
	@uv run mypy app
	@echo "4. Running tests..."
	@$(MAKE) test
	@echo "All CI checks passed!"

# Maintenance
clean:
	docker compose down -v --rmi local
	docker compose -f docker-compose.prod.yml down -v --rmi local

prune:
	docker system prune -af --volumes
