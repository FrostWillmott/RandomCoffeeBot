# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RandomCoffeeBot is a Telegram bot for organizing random coffee meetings between participants. Built with Python 3.12+, it uses aiogram 3 for Telegram bot functionality, SQLAlchemy with asyncpg for async database operations, and APScheduler for background task scheduling.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
pre-commit install
```

### Running the Bot

**Local:**
```bash
python -m app.main
```

**Docker:**
```bash
# Development
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml up -d

# Or use Makefile
make dev          # Start dev environment
make prod         # Start production
```

### Database Migrations

**Local:**
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

**Docker:**
```bash
make migrate                        # Run migrations
make makemigration MSG="description"  # Create migration
```

### Code Quality

```bash
# Linting and formatting
ruff check .
ruff format .

# Type checking
mypy .

# Run all pre-commit hooks
pre-commit run --all-files
```

### Testing

**Local:**
```bash
# Basic test run (coverage enabled by default in pytest.ini)
pytest

# With options
pytest -v                    # Verbose
pytest tests/test_file.py    # Single file
pytest -k test_function      # Specific test
pytest --no-cov              # Disable coverage for faster runs
```

**Docker/Makefile:**
```bash
make test              # Run all tests (auto-manages test DB)
make test-coverage     # Generate coverage report
make test-watch        # Watch mode (re-run on changes)
make test-db-up        # Manually start test DB (port 5433)
make test-db-down      # Stop test DB
```

**Test Database:**
- Separate PostgreSQL instance on port 5434
- Defined in `docker-compose.test.yml`
- Database URL: `postgresql+asyncpg://postgres:postgres@localhost:5434/randomcoffee_test`
- `make test` automatically starts/stops test DB
- Test DB uses tmpfs for faster in-memory storage

**Test Structure:**
- **Unit tests** (`tests/unit/`): Use mocks, no real DB
- **Integration tests** (`tests/integration/`): Use real test DB
- **E2E tests** (`tests/integration/test_e2e_flow.py`): Full scenario tests
- **Factory fixtures** in `conftest.py`: `user_factory`, `session_factory`, `topic_factory`

## Architecture

### Application Lifecycle

The bot follows a structured initialization and shutdown sequence managed in `app/main.py`:

1. **Initialization**: Bot and Dispatcher are created, Scheduler is set up, heartbeat monitoring begins
2. **Runtime**: Bot polls for Telegram updates, scheduler executes background tasks
3. **Shutdown**: Heartbeat stops, scheduler shuts down gracefully, bot session closes

### Configuration Management

**Pattern**: Settings are managed via Pydantic Settings (`app/config.py`) with `.env` file support.

- Settings loaded from environment variables with `.env` file fallback
- Cached using `@lru_cache` via `get_settings()`
- Production validation enforces `SECRET_KEY` and `TELEGRAM_BOT_TOKEN` when `DEBUG=False`
- Configuration accessed globally: `settings = get_settings()`

**Key settings**:
- `telegram_bot_token`: Bot authentication token
- `database_url`: PostgreSQL connection string (format: `postgresql+asyncpg://user:pass@host:port/db`)
- `redis_url`: Redis connection string for FSM storage (format: `redis://host:port/db`)
- `debug`: Enables SQL echo and relaxes production validation
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `log_format`: Log format ("json" for structured logs in production, "text" for development)
- `healthcheck_heartbeat_file`: File path for health monitoring (default: `/tmp/healthy`)

### Database Architecture

**Pattern**: Async SQLAlchemy with automatic transaction management.

**Session Management** (`app/db/session.py`):
- Engine created with connection pooling (pool_size=5, max_overflow=10)
- `get_db()` yields async sessions with auto-commit/rollback
- All database access should use `async with` pattern with `get_db()`

**Models** (`app/models/`):
- Inherit from `app.db.base.Base` (SQLAlchemy DeclarativeBase)
- Import all models in `app/models/__init__.py` for Alembic to discover them

**Migrations** (`alembic/`):
- `alembic/env.py` configured for async operations and auto-discovers models via `Base.metadata`
- Database URL dynamically set from settings
- Migrations run in async mode by default

### Bot Structure

**Bot Initialization** (`app/bot/__init__.py`):
- `get_bot()`: Returns Bot instance with HTML parse mode
- `get_dispatcher()`: Returns Dispatcher with RedisStorage for FSM state persistence
- Routers should be registered in `get_dispatcher()` via `dp.include_router()`

**Handlers** (`app/bot/handlers/`):
- Organized by feature: `start.py`, `registration.py`, `matches.py`, `feedback.py`, `commands.py`
- Each handler file exports a `router` that gets registered in `app/bot/__init__.py`
- Use aiogram's `Router` class and decorator pattern (`@router.message()`, `@router.callback_query()`)

**Middlewares** (`app/bot/middlewares/`):
- `DatabaseMiddleware`: Injects async DB session into handlers automatically
- `ThrottlingMiddleware`: Rate limiting for user actions
- Register middlewares in `get_dispatcher()` before routers

### Background Tasks

**Scheduler** (`app/scheduler.py`):
- Uses APScheduler's AsyncIOScheduler
- Three scheduled jobs configured:
  - `create_weekly_session`: Every Monday at 10:00 UTC (creates session and posts announcement)
  - `close_registrations`: Every hour at :00 (closes expired sessions)
  - `run_matching`: Every hour at :15 (creates matches for closed sessions)
- Jobs are defined in `setup_scheduler(bot)`, started with `start_scheduler()`, shut down with `shutdown_scheduler()`
- Add new jobs using:
  ```python
  from apscheduler.triggers.cron import CronTrigger
  scheduler.add_job(
      some_async_function,
      CronTrigger(hour=10, minute=0),
      args=[bot],  # Pass bot instance if needed
      id="task_id",
      replace_existing=True
  )
  ```

### Repository Layer

**Pattern**: Data access abstraction using the Repository pattern.

**Repositories** (`app/repositories/`):
- `BaseRepository`: Generic CRUD operations (get_by_id, get_all, create, update, delete)
- Domain-specific repositories: `UserRepository`, `SessionRepository`, `MatchRepository`, `RegistrationRepository`, `TopicRepository`, `FeedbackRepository`
- Repositories receive an `AsyncSession` in their constructor
- Services should use repositories instead of direct session queries

### Service Layer

**Pattern**: Business logic separated from handlers into service modules.

**Services** (`app/services/`):
- `sessions.py`: Session creation and management (`create_weekly_session()`)
- `matching.py`: Match creation and registration closing (`create_matches_for_session()`, `close_registration_for_expired_sessions()`, `run_matching_for_closed_sessions()`)
- `notifications.py`: Sending match notifications to users
- `announcements.py`: Posting session announcements to channels
- Services use repositories for data access or accept a session parameter

### Health Monitoring

**Heartbeat System**:
- `run_heartbeat()` in `app/main.py` writes to `/tmp/healthy` every 15 seconds
- Used by Docker healthcheck (`docker/healthcheck.py`)
- Indicates bot process is running and responsive

### Error Handling & Logging

**Logging Configuration** (`app/main.py`):
- Configured at startup based on `LOG_FORMAT` and `LOG_LEVEL` settings
- **JSON format** (production): Structured logs via `pythonjsonlogger` for log aggregation systems
- **Text format** (development): Human-readable console output
- Always use `logger.exception()` for errors to include stack traces

**Pattern for background tasks:**
```python
try:
    logger.info("Starting task...")
    result = await some_operation()
    logger.info("Task completed")
except Exception as e:
    logger.exception("Task failed", exc_info=e)
```

**Database session error handling:**
- Automatic rollback on exception (handled by `get_db()` context manager)
- No need for explicit try/except in most cases
- Transaction automatically commits on success

## Code Style

- **Line length**: 92 characters (configured in `ruff.toml`)
- **Quotes**: Double quotes for strings and docstrings
- **Docstrings**: Google style convention
- **Type hints**: Required for all function signatures
- **Import sorting**: Enforced by ruff (isort)
- **Docstrings**: Required for public modules, classes, and functions (pydocstyle D rules)

## Important Patterns

### Adding New Models

1. Create model in `app/models/your_model.py` inheriting from `Base`
2. Import in `app/models/__init__.py`
3. Generate migration: `alembic revision --autogenerate -m "add your_model"`
4. Review and run migration: `alembic upgrade head`

### Adding Bot Handlers

1. Create new file in `app/bot/handlers/your_feature.py`
2. Create a router and define handlers:
   ```python
   from aiogram import Router, F
   from aiogram.types import Message, CallbackQuery
   from sqlalchemy.ext.asyncio import AsyncSession

   router = Router()

   @router.message(F.text == "/command")
   async def handler(message: Message, session: AsyncSession):
       # Session auto-injected by DatabaseMiddleware
       pass
   ```
3. Register router in `app/bot/__init__.py` in `get_dispatcher()`:
   ```python
   from app.bot.handlers import your_feature
   dp.include_router(your_feature.router)
   ```

### Database Operations

**In service layer functions:**
```python
from app.db.session import get_db

async def some_operation():
    async for session in get_db():
        # Auto-commits on success, rolls back on exception
        result = await session.execute(query)
        return result
```

**In handlers (session injected by middleware):**
```python
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.message()
async def handler(message: Message, session: AsyncSession):
    # Session is auto-injected by DatabaseMiddleware
    # Still auto-commits on success, rolls back on exception
    result = await session.execute(query)
```

### Accessing Configuration

```python
from app.config import get_settings

settings = get_settings()  # Cached singleton
token = settings.telegram_bot_token
```

## Security Best Practices

**Environment Files:**
- `.env` - Local working file with real secrets (gitignored, NEVER commit)
- `.env.example` - Template for both local and Docker development (tracked, placeholders only)
- `.env.prod.example` - Template for production (tracked, placeholders only)

**Setup Process:**
1. User copies template: `cp .env.example .env`
2. User edits `.env` with real tokens/passwords
3. For local dev: change DATABASE_URL host from `db` to `localhost`
4. `.env` stays local, never goes to git

**IMPORTANT:** Template files (*.example) must NEVER contain real tokens or passwords.

## Development Notes

- Package manager is `uv` (not pip)
- Pre-commit hooks run ruff (lint + format) and mypy automatically
- Tests use pytest with async support (pytest-asyncio with `asyncio_mode = auto`)
- Test database runs on port 5434 (separate from dev DB on 5432)
- Minimum test coverage required: 80% (enforced by pytest)
- The project uses Python 3.12+ features and type hints throughout
- FSM storage uses Redis (RedisStorage), state persists across restarts
- When making commits, do NOT add Claude Code as co-author

## Key Domain Concepts

**Session Lifecycle:**
1. **OPEN**: Registration is open, users can register
2. **CLOSED**: Registration deadline passed, matching in progress
3. **MATCHED**: Matches created, notifications sent
4. **COMPLETED**: Session finished, feedback collected

**Match Status:**
- `PENDING`: Match created, waiting for confirmation
- `CONFIRMED`: Both users confirmed (not currently enforced)
- `COMPLETED`: Meeting happened, feedback may be given
- `CANCELLED`: Match was cancelled

**Matching Algorithm:**
- Greedy algorithm that tries to avoid repeat pairings
- Fetches previous matches from all sessions
- Shuffles registrations and pairs sequentially
- Falls back to repeat pairing if no fresh matches available
- Random topic assignment to each match
- Returns count of matches created + list of unmatched user IDs
