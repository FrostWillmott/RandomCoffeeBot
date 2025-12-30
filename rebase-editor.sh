#!/bin/bash
# Автоматический редактор для git rebase

REBASE_TODO="$1"

cat > "$REBASE_TODO" << 'EOF'
pick 6886bd7 feat: implement Random Coffee Bot MVP
squash 83fa773 Alfa test MVP
squash faff7f8 Alfa test MVP
squash e4d61b3 Alfa test MVP
pick 02a78ec Fix CI: add env vars for tests and remove coverage threshold
squash 57ae1ab ci: refactor test workflow and fix test environment setup
squash e04c5d2 ci: export deps without editable for pip-audit
squash 71d009c fix: align scheduler with UTC and enforce security scans
pick 09e8b01 refactor(core): migrate to Clean Architecture
squash 8fea732 fix: resolve mypy type checking errors in repositories
squash 3e6f42e fix: update tests to match refactored repository layer
pick 8049f43 fix(security): add authorization checks for match and feedback handlers
squash 644e6e0 fix: handle race condition in registration and prevent duplicate feedback
squash 288334c fix: throttle race and rollback on dup registration
squash ee3280c fix: use bot from reaction context to prevent HTTP session leak
pick d4542d5 fix: correct 3 bugs found by cursor review
squash 8f55981 fix(helpers): prevent exception with multiple open sessions
squash e4e0f83 fix(feedback): correct user ID lookup and callback prefixes
squash 5eefb8b fix: handle legacy keyboard buttons and unknown callbacks
squash 3e557df fix: remove legacy ReplyKeyboard buttons from previous bot
squash f8f6a47 test: fix mocks for get_next_open_session after .limit(1) change
pick 461dddc db: remove redundant performance indexes
squash ebd02ce chore: add postgres password env to dev compose
pick e93a82d style: add explanatory comments to silent except blocks
squash b81892a fix: stop reprocessing small sessions and close redis
squash 57d2526 fix: remove invalid redis wait_closed call
pick 590eefb fix: add REDIS_URL configuration for Docker
EOF

exit 0

