# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Telegram bot that organizes random coffee meetings — creates weekly sessions, matches participants into pairs/triplets, assigns discussion topics, and sends notifications. Built with aiogram 3, PostgreSQL + SQLAlchemy 2 async, Redis for FSM, and APScheduler for background jobs.

## Commands

```bash
make dev           # Start dev environment (Docker)
make down          # Stop dev containers
make logs          # View bot logs
make test          # Run all tests (auto-manages test DB container)
make test-coverage # Run tests with coverage (gate: 80%)
make lint          # ruff check
make format        # ruff format
make typecheck     # mypy app (--strict)
make ci            # All checks: lint + format-check + typecheck + test
make migrate       # Apply Alembic migrations
make makemigration MSG='description'  # Create new migration
make db-seed       # Seed discussion topics
```

Run a single test: `uv run pytest tests/path/test_file.py::test_name -v`

## Architecture

**Layers** (dependencies point inward): Handlers → Services → Repositories → Models.

**Protocol-based DI** — services accept repository protocols (`UserRepositoryProtocol`, etc.), not concrete classes. This is the central pattern. Concrete repositories are created at the call site (handler middleware or scheduler entry point) and passed in.

**Services are standalone async functions**, not classes. Each service function accepts typed repository protocols. Example:
```python
async def create_matches_for_session(
    session_id: int,
    match_repo: MatchRepositoryProtocol,
    ...
) -> tuple[int, list[int]]:
```

**Repository protocols** live in `app/repositories/protocols.py`. Concrete implementations are in `app/repositories/*.py`. When adding a new data access method, declare it in the protocol first, then implement.

**Scheduler as orchestrator** — `app/scheduler.py` separates matching (pure data logic in `app/services/matching.py`) from notifications (Telegram API in `app/services/notifications.py`). Recovery jobs handle fault tolerance:
- `recover_unannounced_sessions` — picks up sessions created but not announced (hourly at :30)
- `recover_unnotified_matched_sessions` — picks up matched sessions without notifications (hourly at :45)

**Session lifecycle**: OPEN → CLOSED (registration deadline passed) → MATCHING (claimed atomically via `UPDATE ... WHERE status = 'CLOSED'`) → MATCHED → COMPLETED.

**Atomic claim** (`SessionRepository.claim_for_matching`) is the concurrency safeguard — exactly one caller gets the row back. Do not weaken this without understanding the implications.

**Explicit session management** — the caller owns the transaction. `DatabaseMiddleware` provides `AsyncSession` per update; scheduler entry points create their own sessions. Services never commit.

**Bot setup** — `app/bot/__init__.py::get_dispatcher()` wires routers and middlewares. Add new handlers as a router file in `app/bot/handlers/`, then register it there.

## Key conventions

- `from __future__ import annotations` in every module
- Modern type hints: `list[X]`, `dict[K, V]`, `X | None` (not `typing.List`, `Optional`)
- `mypy --strict` with per-module overrides in `pyproject.toml` — no `type: ignore` without a reason comment
- ruff with explicit `select` in `ruff.toml` (line length 92, double quotes, Google-style docstrings)
- Tests mirror source tree: `tests/unit/` (fast, mocked), `tests/integration/` (real PostgreSQL)
- Settings via `app/config.py::get_settings()` — Pydantic Settings, `.env` file, `@lru_cache` singleton
- `uv` for package management; `pyproject.toml` dependency groups for dev dependencies
