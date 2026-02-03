# Random Coffee Bot

Telegram bot for organizing random coffee meetings between participants.

## Features

- Telegram bot built with aiogram 3
- PostgreSQL database with SQLAlchemy ORM
- Async database operations with asyncpg
- Database migrations with Alembic
- Background task scheduling with APScheduler
- Docker support for easy deployment
- Automated code quality checks with Ruff
- Type checking with mypy
- Pre-commit hooks for code consistency
- Comprehensive test suite (unit and integration tests)
- Support for pair and triplet matching
- Topic-based conversation starters

## Requirements

- Python 3.12+
- uv (package manager)
- PostgreSQL 13+ (or use Docker)
- Telegram Bot Token (from @BotFather)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/FrostWillmott/RandomCoffeeBot.git
cd RandomCoffeeBot
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
uv sync --all-extras
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env:
# - Add your TELEGRAM_BOT_TOKEN from @BotFather
# - Change DATABASE_URL host from 'db' to 'localhost' for local development
```

6. Run database migrations:
```bash
alembic upgrade head
```

### Docker Development

1. Copy environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your TELEGRAM_BOT_TOKEN from @BotFather

3. Start services:
```bash
docker-compose up -d
```

## Usage

### Local Development
```bash
python -m app.main
```

### Docker
```bash
docker-compose up
```

### With Makefile
```bash
make run          # Run locally
make dev          # Start development environment with Docker
make down         # Stop Docker services
make test         # Run tests (auto-manages test DB)
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


## Security Best Practices

When deploying RandomCoffeeBot in production:

### Environment Variables
- ✅ Always use strong, randomly generated values for `SECRET_KEY`
- ✅ Never commit `.env` files to version control
- ✅ Rotate credentials regularly
- ✅ Use separate credentials for dev/staging/production

### Database
- ✅ Use strong passwords for PostgreSQL
- ✅ Restrict database access to application containers only
- ✅ Enable SSL/TLS for database connections in production
- ✅ Regularly backup your database

### Network
- ✅ Use firewall rules to restrict access
- ✅ Only expose necessary ports
- ✅ Use reverse proxy (nginx) in production
- ✅ Enable HTTPS for any HTTP endpoints

### Docker
- ✅ Don't expose ports publicly (use `127.0.0.1:port:port`)
- ✅ Scan images for vulnerabilities regularly
- ✅ Keep base images up to date
- ✅ Use Docker secrets for sensitive data in Swarm/K8s

### Dependencies
- ✅ Keep dependencies up to date
- ✅ Review Dependabot alerts promptly
- ✅ Use `uv` lock file to ensure reproducible builds

### Monitoring
- ✅ Monitor logs for suspicious activity
- ✅ Set up alerting for errors and anomalies
- ✅ Regularly review access logs

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all pre-commit checks pass
5. Submit a merge request
