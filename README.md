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

## Requirements

- Python 3.12+
- uv (package manager)
- PostgreSQL 13+ (or use Docker)
- Telegram Bot Token (from @BotFather)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://gitlab.com/FrostWillmott/RandomCoffeeBot.git
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
# Edit .env and add your TELEGRAM_BOT_TOKEN and DATABASE_URL
```

6. Run database migrations:
```bash
alembic upgrade head
```

### Docker Development

1. Copy environment file:
```bash
cp .env.dev .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

2. Start services:
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
make docker-up    # Run with Docker
make docker-down  # Stop Docker services
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


## Project Structure

```
RandomCoffeeBot/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── bot.py           # Bot initialization
│   ├── config.py        # Configuration management
│   ├── scheduler.py     # Background task scheduler
│   ├── db/              # Database configuration
│   │   ├── session.py   # Database session management
│   │   └── base.py      # SQLAlchemy base class
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── alembic/             # Database migrations
├── docker/              # Docker configuration
├── deploy/              # Deployment configs
├── docker-compose.yml   # Docker Compose for development
├── docker-compose.prod.yml  # Docker Compose for production
├── Makefile             # Common commands
├── pyproject.toml       # Project metadata and dependencies
├── ruff.toml            # Ruff linter configuration
└── .pre-commit-config.yaml  # Pre-commit hooks
```


## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all pre-commit checks pass
5. Submit a merge request
```
