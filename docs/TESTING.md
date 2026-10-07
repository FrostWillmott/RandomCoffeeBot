# Testing

This guide covers how the test suite is structured, configured, and run. For a manual
smoke check against a real bot and channel, see
[docs/MANUAL_TESTING.md](MANUAL_TESTING.md).

## Test database configuration

Tests use a **separate PostgreSQL container** for complete isolation from
production data.

- **Separate container:** `randomcoffee-db-test` on port `5434`
- **Separate DB:** `randomcoffee_test`
- **Transactional isolation:** each test runs in its own transaction that is
  rolled back on completion
- **In-memory storage:** `tmpfs` is used for speed (data does not persist)

### Environment variables

Configured in `tests/conftest.py`:

- `TEST_DATABASE_NAME` - test DB name (default: `randomcoffee_test`)
- `TEST_DATABASE_HOST` - DB host (default: `localhost`)
- `TEST_DATABASE_PORT` - DB port (default: `5434`; production uses `5432`)
- `TEST_DATABASE_USER` - DB user (default: `postgres`)
- `TEST_DATABASE_PASSWORD` - DB password (default: `postgres`)
- `TEST_DATABASE_URL` - full test DB URL (overrides the fields above)
- `TEST_DATABASE_BASE_URL` - URL to the `postgres` DB, used to create the test DB

## Test structure

Tests are split into two categories:

### Unit tests (`tests/unit/`) — mocked, no database

Fast tests that mock external resources for isolation:

- `test_announcements_mocked.py` - announcements service
- `test_config.py` - configuration
- `test_matching_functions.py` - matching service
- `test_notifications_mocked.py` - notifications service
- `test_reactions_handler.py` - reaction handling
- `test_scheduler.py` - task scheduler
- `test_schemas_callbacks.py` - callback data schemas
- `test_sessions_mocked.py` - sessions service
- `test_utils_retry.py` - retry utilities

### Integration tests (`tests/integration/`) — real database

Tests that verify real database integration and complex business logic:

- `test_e2e_flow.py` - end-to-end registration and matching flow
- `test_matching.py` - matching algorithm and the atomic claim
- `test_sessions.py` - sessions service

## Running tests

### With the Makefile (recommended)

```bash
make test              # Run all tests (auto-manages the test DB container)
make test-coverage     # Run tests with coverage (gate: 80%)
make test-watch        # Run tests in watch mode
```

### Manually

```bash
# Start the test DB
make test-db-up
# or
docker-compose -f docker-compose.test.yml up -d db-test

# Run tests
uv run pytest tests/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=html

# Stop the test DB
make test-db-down
# or
docker-compose -f docker-compose.test.yml down
```

## Coverage

Overall coverage is tracked by the badge in the README and enforced at 80% in
CI. Per-module detail is available via `pytest --cov=app --cov-report=term`.

## Async mocking: why `session.add()` is a `MagicMock`, not an `AsyncMock`

In SQLAlchemy's `AsyncSession`, methods that only touch in-memory state are
synchronous, while I/O methods are coroutines:

- **Synchronous:** `add()`, `delete()`, `expire()`, `expire_all()`
- **Asynchronous:** `execute()`, `commit()`, `rollback()`, `flush()`, `refresh()`

`session.add()` only registers an object with the session and does not perform
any I/O, so it is not a coroutine. Mocking it as `AsyncMock` (which makes every
method a coroutine) produces a coroutine that is never awaited.

### Correct

```python
mock_session = AsyncMock()
mock_session.add = MagicMock()        # synchronous method
mock_session.execute = AsyncMock()    # asynchronous method
mock_session.commit = AsyncMock()     # asynchronous method
mock_session.flush = AsyncMock()      # asynchronous method
```

### Incorrect

```python
mock_session = AsyncMock()  # makes EVERY method a coroutine
# session.add() becomes a coroutine that is never awaited
```

All `session.add()` call sites in the project are `await`-free (e.g.
`app/repositories/base.py`), so the mock must match the real API.

## Troubleshooting

**DB connection error:**

```bash
docker-compose -f docker-compose.test.yml ps
docker-compose -f docker-compose.test.yml logs db-test
psql -h localhost -p 5434 -U postgres -d randomcoffee_test
```

**Port conflict:** ensure port `5434` is free, or change `TEST_DATABASE_PORT`.

**Tests are not isolated:** verify the `db_session` fixture is used and that
transactions roll back (see `tests/conftest.py`), and that the correct port is
used (`5434`, not `5432`).
