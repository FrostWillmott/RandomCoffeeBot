# Testing

## Test Database Configuration

Tests use a **separate PostgreSQL container** for complete isolation from production data.

### Test Isolation

1. **Separate Container:** `randomcoffee-db-test` on port 5434
2. **Separate DB:** `randomcoffee_test` (isolated from production)
3. **Transactional Isolation:** Each test runs in a separate transaction that automatically rolls back upon completion
4. **Automatic Cleanup:** Data does not accumulate between tests
5. **In-memory Storage:** tmpfs is used for speed

### Quick Start

#### Using Makefile (Recommended)

```bash
# Run tests (automatically starts/stops the test DB)
make test

# Run tests with coverage
make test-coverage

# Run tests in watch mode
make test-watch
```

#### Manual Management

```bash
# Start the test DB
make test-db-up
# or
docker-compose -f docker-compose.test.yml up -d db-test

# Run tests
uv run pytest tests/ -v

# Stop the test DB
make test-db-down
# or
docker-compose -f docker-compose.test.yml down
```

### Configuration

#### Environment Variables

- `TEST_DATABASE_NAME` - test DB name (default: `randomcoffee_test`)
- `TEST_DATABASE_HOST` - DB host (default: `localhost`)
- `TEST_DATABASE_PORT` - DB port (default: `5434` - separate from production at 5432)
- `TEST_DATABASE_USER` - DB user (default: `postgres`)
- `TEST_DATABASE_PASSWORD` - DB password (default: `postgres`)
- `TEST_DATABASE_URL` - full test DB URL (overrides all the above)
- `TEST_DATABASE_BASE_URL` - URL to connect to the postgres DB (for creating the test DB)

### Running Tests

```bash
# All tests (with automatic DB management)
make test

# All tests (if the DB is already running)
uv run pytest tests/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# With code coverage
make test-coverage
# or
uv run pytest tests/ --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py                    # Configuration and fixtures
├── unit/                          # Unit tests (~82 tests)
│   ├── test_announcements_mocked.py
│   ├── test_config.py
│   ├── test_db_session.py
│   ├── test_helpers_mocked.py
│   ├── test_matching_functions.py
│   ├── test_notifications_mocked.py
│   ├── test_reactions_handler.py
│   ├── test_scheduler.py
│   ├── test_schemas_callbacks.py
│   ├── test_sessions_mocked.py
│   ├── test_utils_context.py
│   └── test_utils_retry.py
└── integration/                   # Integration tests (~18 tests)
    ├── test_e2e_flow.py
    ├── test_helpers.py
    ├── test_matching.py
    └── test_sessions.py
```

### Important Points

1. **Isolation:** Each test is isolated via transactions
2. **Automatic Cleanup:** No need to manually delete data
3. **Speed:** Transactions are faster than a full DB cleanup
4. **Security:** The production DB is never used for tests

### Advantages of the Current Configuration

1. **Full Isolation:** Separate container, separate port, separate DB
2. **Speed:** tmpfs for in-memory storage
3. **Automation:** Makefile commands for convenience
4. **Security:** Production DB is never used
5. **Parallelism:** Tests can be run in parallel with production

### Troubleshooting

**DB Connection Error:**
```bash
# Verify that the test DB is running
docker-compose -f docker-compose.test.yml ps

# Check logs
docker-compose -f docker-compose.test.yml logs db-test

# Check connection
psql -h localhost -p 5434 -U postgres -d randomcoffee_test
```

**Port Conflict:**
- Ensure port 5434 is free
- Or change `TEST_DATABASE_PORT` in environment variables

**Tests are not isolated:**
- Ensure the `db_session` fixture is used
- Verify that transactions are rolled back (see `conftest.py`)
- Ensure the correct port is being used (5434 instead of 5432)
