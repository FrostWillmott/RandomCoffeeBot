# Random Coffee Bot

[![CI](https://github.com/FrostWillmott/RandomCoffeeBot/actions/workflows/ci.yml/badge.svg)](https://github.com/FrostWillmott/RandomCoffeeBot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/FrostWillmott/RandomCoffeeBot/branch/master/graph/badge.svg)](https://codecov.io/gh/FrostWillmott/RandomCoffeeBot)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Telegram bot that automatically organizes random coffee meetings between community members. The bot creates pairs/triplets, assigns discussion topics, manages registrations, and sends notifications — helping people connect and learn together.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.12+, asyncio |
| Bot Framework | aiogram 3 |
| Database | PostgreSQL 16 + SQLAlchemy 2 (async) |
| State Storage | Redis (FSM persistence) |
| Scheduling | APScheduler |
| Migrations | Alembic |
| Testing | pytest + pytest-asyncio, 81%+ coverage |
| CI/CD | GitHub Actions, Docker, Codecov |
| Code Quality | ruff, mypy, pre-commit |

### Architecture Decisions

1. **Protocol-based Dependency Injection** — services accept repository protocols (`SessionRepositoryProtocol`, etc.) instead of concrete classes. This decouples business logic from data access, makes unit testing trivial with `AsyncMock`, and follows the Dependency Inversion Principle without a DI container.

2. **Matching decoupled from notifications** — `run_matching_for_closed_sessions()` returns pure data (`SessionMatchResult`), and the scheduler orchestrates notification dispatch separately. This keeps the matching algorithm free of Telegram API dependencies, simplifying testing and future transport changes.

3. **Atomic session claiming with `MATCHING` status** — before creating matches, a session transitions `CLOSED → MATCHING` via an atomic `UPDATE ... WHERE status = 'CLOSED'`. Only one worker gets `rowcount > 0`, preventing duplicate matches in concurrent environments without distributed locks.

4. **Explicit session management** — services never create their own database sessions. The caller (handler middleware or scheduler entry point) owns the session lifecycle, giving full control over transaction boundaries and commit/rollback semantics.

5. **Layered architecture** — Handlers → Services → Repositories → Models. Each layer depends only on abstractions of the layer below. Domain logic in services is framework-agnostic and sync-compatible by design.

## Quick Start

Get the bot running in under 2 minutes:

1. **Get a Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

3. **Start with Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Seed topics (optional but recommended):**
   ```bash
   make db-seed
   ```

5. **Start chatting** with your bot in Telegram!

The bot will automatically create weekly sessions, manage registrations, and match participants.

## How It Works

### For Participants

1. **Registration**: React with 👍 on the announcement in your channel or use `/start` command
2. **Get Matched**: Every week the bot creates random pairs/triplets
3. **Receive Topic**: Get a discussion topic for your meeting (e.g., "Python Decorators", "Async Programming")
4. **Meet & Learn**: Have your coffee chat and discuss the topic
5. **Give Feedback**: Rate your experience and help improve matching

### Available Commands

- `/start` - Register for the next Random Coffee session
- `/help` - Get information about how the bot works
- `/status` - Check your registration status and upcoming matches
- `/cancel` - Cancel your registration for the current session

### Automated Workflow

The bot runs on a weekly schedule:
- **Monday 10:00 UTC** - Creates new session and posts announcement to channel
- **Every hour** - Closes registrations for expired sessions
- **Every hour** - Creates matches for closed sessions and sends notifications

## Features

- 🤖 Automated weekly session creation and announcements
- 👥 Smart matching algorithm (avoids repeat pairings, supports pairs and triplets)
- 💬 Topic-based conversation starters for every meeting
- 📊 Registration management via reactions or commands
- 🔔 Automatic notifications when matches are created
- ⭐ Feedback system to improve future matches
- 🐳 Docker-ready deployment
- 🧪 Comprehensive test coverage (81%+)

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture, data flows, and technical design
- **[docs/MANUAL_TESTING.md](docs/MANUAL_TESTING.md)** - Complete testing guide for QA
- **[docs/TOPICS_DESIGN.md](docs/TOPICS_DESIGN.md)** - Discussion topics system design
- **[tests/README.md](tests/README.md)** - Developer testing guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

## Requirements

- Docker & Docker Compose (recommended)
- OR Python 3.12+ with PostgreSQL 13+ (for local development)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram Channel (for announcements)

## Installation & Development

### Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/FrostWillmott/RandomCoffeeBot.git
cd RandomCoffeeBot

# Configure environment
cp .env.example .env
# Edit .env and set:
# - TELEGRAM_BOT_TOKEN (from @BotFather)
# - CHANNEL_ID (your announcement channel)

# Start all services
docker-compose up -d

# Seed discussion topics
make db-seed

# View logs
make logs
```

### Local Development (Without Docker)

1. **Prerequisites:**
   - Python 3.12+
   - PostgreSQL 13+
   - Redis (for FSM state)
   - [uv](https://github.com/astral-sh/uv) package manager

2. **Setup:**
   ```bash
   # Clone and install
   git clone https://github.com/FrostWillmott/RandomCoffeeBot.git
   cd RandomCoffeeBot
   uv sync --all-extras

   # Install pre-commit hooks
   pre-commit install

   # Configure environment
   cp .env.example .env
   # Edit .env:
   # - Add TELEGRAM_BOT_TOKEN
   # - Change DATABASE_URL host from 'db' to 'localhost'
   # - Set REDIS_URL to redis://localhost:6379/0

   # Run migrations
   alembic upgrade head

   # Seed topics
   uv run python scripts/seed_topics.py

   # Start bot
   python -m app.main
   ```

### Common Commands

```bash
make dev           # Start development environment (Docker)
make down          # Stop all services
make logs          # View bot logs
make migrate       # Run database migrations
make db-seed       # Load discussion topics
make test          # Run tests
make db-shell      # Open PostgreSQL shell
```

## Development

### Code Quality

This project uses:
- **Ruff** for linting and formatting
- **mypy** for static type checking
- **pre-commit** for automated checks before commits

Run checks manually:
```shell script
ruff check .
ruff format .
mypy .
```


### Pre-commit

Pre-commit hooks run automatically on `git commit`. To run on all files:
```shell script
pre-commit run --all-files
```

### Testing

The project includes comprehensive test coverage (81%+):

```bash
make test              # Run all tests (auto-manages test DB)
make test-coverage     # Run tests with coverage report
make test-watch        # Run tests in watch mode
```

Tests are organized into:
- **Unit tests** (`tests/unit/`) - Fast tests with mocks
- **Integration tests** (`tests/integration/`) - Tests with real database

See [tests/README.md](tests/README.md) for more details.


## Project Structure

```
RandomCoffeeBot/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration management
│   ├── constants.py     # Application constants
│   ├── scheduler.py     # Background task scheduler
│   ├── bot/             # Bot components
│   │   ├── __init__.py  # Bot initialization
│   │   ├── handlers/    # Message and callback handlers
│   │   ├── keyboards/   # Inline keyboards
│   │   ├── middlewares/ # Middleware (database, throttling)
│   │   └── states/      # FSM states
│   ├── db/              # Database configuration
│   │   ├── session.py   # Database session management
│   │   └── base.py      # SQLAlchemy base class
│   ├── models/          # SQLAlchemy models
│   ├── repositories/    # Data access layer
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── alembic/             # Database migrations
├── docker/              # Docker configuration
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── scripts/             # Utility scripts
├── docker-compose.yml   # Docker Compose for development
├── docker-compose.prod.yml  # Docker Compose for production
├── docker-compose.test.yml  # Docker Compose for tests
├── Makefile             # Common commands
├── pyproject.toml       # Project metadata and dependencies
├── ruff.toml            # Ruff linter configuration
└── .pre-commit-config.yaml  # Pre-commit hooks
```


## Deployment

### Production Deployment

1. **Prepare production environment:**
   ```bash
   cp .env.prod.example .env.prod
   # Edit .env.prod with production values:
   # - Strong SECRET_KEY (generate with: openssl rand -hex 32)
   # - Production DATABASE_URL
   # - REDIS_URL
   # - DEBUG=False
   # - LOG_FORMAT=json
   ```

2. **Deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run migrations:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec bot alembic upgrade head
   ```

4. **Seed topics:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec bot python scripts/seed_topics.py
   ```

5. **Set up monitoring:**
   - Monitor logs: `docker-compose -f docker-compose.prod.yml logs -f bot`
   - Check health: `docker-compose -f docker-compose.prod.yml exec bot cat /tmp/healthy`

### Environment Variables

**Required:**
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `CHANNEL_ID` - Channel ID or @username for announcements
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string for FSM storage

**Optional:**
- `SECRET_KEY` - Random secret for production (auto-generated if DEBUG=True)
- `DEBUG` - Enable debug mode (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)
- `LOG_FORMAT` - Log format: "json" or "text" (default: text)
- `HEALTHCHECK_HEARTBEAT_FILE` - Health check file path (default: /tmp/healthy)

See `.env.example` for full configuration options.

## Security Best Practices

### Environment & Secrets
- ✅ Use strong, randomly generated `SECRET_KEY` in production
- ✅ Never commit `.env` files to version control
- ✅ Rotate credentials regularly
- ✅ Use separate credentials for dev/staging/production

### Database
- ✅ Use strong passwords for PostgreSQL
- ✅ Restrict database access to application containers only
- ✅ Enable SSL/TLS for database connections in production
- ✅ Regularly backup your database

### Network & Docker
- ✅ Use firewall rules to restrict access
- ✅ Don't expose ports publicly (use `127.0.0.1:port:port`)
- ✅ Use reverse proxy (nginx) in production
- ✅ Scan images for vulnerabilities regularly
- ✅ Keep base images up to date

### Monitoring & Updates
- ✅ Monitor logs for suspicious activity (`LOG_FORMAT=json` in production)
- ✅ Set up alerting for errors and anomalies
- ✅ Keep dependencies up to date
- ✅ Review Dependabot alerts promptly

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all pre-commit checks pass
5. Submit a merge request
