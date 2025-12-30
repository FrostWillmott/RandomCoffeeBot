#!/bin/bash
# Автоматический редактор сообщений коммитов для rebase

COMMIT_MSG_FILE="$1"

# Определяем, какое сообщение нужно создать на основе текущего коммита
CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "")

# Читаем существующее сообщение
if [ -f "$COMMIT_MSG_FILE" ]; then
    EXISTING_MSG=$(cat "$COMMIT_MSG_FILE")
else
    EXISTING_MSG=""
fi

# Определяем тип коммита по существующему сообщению
if echo "$EXISTING_MSG" | grep -q "feat: implement Random Coffee Bot MVP"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
feat: implement Random Coffee Bot MVP

Initial implementation of Random Coffee Bot with core functionality:
- User registration and session management
- Matching algorithm
- Feedback system
- Telegram bot integration
EOF
elif echo "$EXISTING_MSG" | grep -q "Fix CI:"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
ci: improve CI/CD pipeline and test infrastructure

- Add environment variables for tests
- Refactor test workflow
- Fix pip-audit dependency export
- Enforce security scans and UTC timezone for scheduler
EOF
elif echo "$EXISTING_MSG" | grep -q "refactor(core): migrate to Clean Architecture"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
refactor: migrate to Clean Architecture with repository pattern

- Implement repository layer for data access
- Add protocol interfaces for repositories
- Fix mypy type checking errors
- Update tests to use repository mocks
EOF
elif echo "$EXISTING_MSG" | grep -q "fix(security): add authorization checks"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
fix(security): add authorization checks and fix race conditions

- Add user authorization checks for match and feedback handlers
- Handle race conditions in registration with IntegrityError
- Prevent duplicate feedback submissions
- Fix Redis throttling race condition
- Use bot from context to prevent HTTP session leaks
EOF
elif echo "$EXISTING_MSG" | grep -q "fix: correct 3 bugs found by cursor review"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
fix: resolve multiple bugs and improve error handling

- Fix exception with multiple open sessions
- Correct user ID lookup in feedback handlers
- Handle legacy keyboard buttons and unknown callbacks
- Remove legacy ReplyKeyboard buttons
- Fix test mocks after query changes
EOF
elif echo "$EXISTING_MSG" | grep -q "db: remove redundant performance indexes"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
db: optimize database schema and configuration

- Remove redundant indexes that duplicate unique constraints
- Add POSTGRES_PASSWORD to development docker-compose
EOF
elif echo "$EXISTING_MSG" | grep -q "style: add explanatory comments"; then
    cat > "$COMMIT_MSG_FILE" << 'EOF'
refactor: improve code quality and resource management

- Add explanatory comments to silent except blocks
- Fix session reprocessing for insufficient registrations
- Properly close Redis connections on shutdown
- Remove invalid wait_closed() call
EOF
else
    # Используем существующее сообщение
    echo "$EXISTING_MSG" > "$COMMIT_MSG_FILE"
fi

exit 0

