.PHONY: help dev dev-build down logs shell migrate makemigration prod prod-build prod-down prod-logs test lint format clean prune

# Default target
help:
	@echo "RandomCoffeeBot Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make down         - Stop all containers"
	@echo "  make logs         - View container logs"
	@echo "  make shell        - Open shell in bot container"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make makemigration MSG='message' - Create new migration"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production"
	@echo "  make prod-down    - Stop production containers"
	@echo "  make prod-logs    - View production logs"
	@echo ""
	@echo "Quality:"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Remove containers, volumes, images"
	@echo "  make prune        - Docker system prune"

# Development
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

# Database
migrate:
	docker compose exec bot alembic upgrade head

makemigration:
	docker compose exec bot alembic revision --autogenerate -m "$(MSG)"

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
	docker compose exec bot pytest

lint:
	docker compose exec bot ruff check .

format:
	docker compose exec bot ruff format .

# Maintenance
clean:
	docker compose down -v --rmi local
	docker compose -f docker-compose.prod.yml down -v --rmi local

prune:
	docker system prune -af --volumes
