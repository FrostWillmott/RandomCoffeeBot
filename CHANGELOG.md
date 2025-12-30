# Changelog

All notable changes to RandomCoffeeBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Performance indices for database queries (registrations, matches, sessions, topics)
- Enhanced Dependabot configuration with labels, commit message formatting, and dependency grouping
- SECURITY.md with vulnerability reporting process and security best practices
- Comprehensive CLAUDE.md documentation for AI-assisted development
- Integration test suite with factory fixtures and E2E test flows
- GitHub Actions CI/CD workflow with PostgreSQL and Redis services
- Coverage reporting with pytest-cov (88.66% coverage)
- Docker healthcheck system with heartbeat monitoring
- Pre-commit hooks for code quality (ruff, mypy)

### Changed
- Externalized database credentials from docker-compose.yml to environment variables
- Restricted PostgreSQL and Redis port exposure to localhost only
- Improved test database isolation with separate docker-compose.test.yml
- Enhanced test structure with unit/integration separation

### Security
- Removed hardcoded passwords from Docker Compose configuration
- Added mandatory POSTGRES_PASSWORD validation in docker-compose.yml
- Implemented localhost-only port bindings for database services
- Documented security best practices in SECURITY.md

## [0.1.0] - 2025-12-29

### Added
- Initial Random Coffee Bot MVP implementation
- Telegram bot with aiogram 3 framework
- User registration and profile management
- Automated random matching algorithm
- Session scheduling with APScheduler
- Topic selection system for conversation starters
- Match feedback collection
- PostgreSQL database with SQLAlchemy async ORM
- Redis-based FSM storage for bot state
- Alembic migrations for database schema management
- Docker support for development and production environments
- Comprehensive documentation (README, ARCHITECTURE, TOPICS_DESIGN)
- Rate limiting via ThrottlingMiddleware
- Channel announcements support
- Health monitoring system

### Technical Stack
- Python 3.12+
- aiogram 3.x (Telegram bot framework)
- SQLAlchemy 2.x with asyncpg (async PostgreSQL driver)
- PostgreSQL 16
- Redis 7
- APScheduler (background task scheduling)
- Docker & Docker Compose
- Alembic (database migrations)
- pytest with asyncio support

---

For migration guides and upgrade instructions, see [ARCHITECTURE.md](ARCHITECTURE.md).
For security-related updates, see [SECURITY.md](SECURITY.md).
