# Предложение по улучшению истории коммитов

> **Примечание:** Это исторический документ с рекомендациями по улучшению истории коммитов. Может быть устаревшим.

## Текущие проблемы

1. **Дублирующиеся коммиты**: Три коммита "Alfa test MVP" (e4d61b3, faff7f8, 83fa773)
2. **Мелкие коммиты**: Много мелких фиксов, которые можно объединить
3. **Непоследовательность**: Смешение стилей сообщений (с префиксами и без)
4. **Группировка**: Связанные изменения разбросаны по разным коммитам

## Предлагаемая структура коммитов

### 1. Объединить дублирующиеся коммиты MVP
```
Было:
* e4d61b3 Alfa test MVP
* faff7f8 Alfa test MVP
* 83fa773 Alfa test MVP
* 6886bd7 feat: implement Random Coffee Bot MVP

Стало:
* 6886bd7 feat: implement Random Coffee Bot MVP
```

### 2. Группировка связанных фиксов

#### Группа: CI/CD и инфраструктура
```
Объединить:
* 02a78ec Fix CI: add env vars for tests and remove coverage threshold
* 57ae1ab ci: refactor test workflow and fix test environment setup
* e04c5d2 ci: export deps without editable for pip-audit
* 71d009c fix: align scheduler with UTC and enforce security scans

В один коммит:
* ci: improve CI/CD pipeline and test infrastructure
  - Add environment variables for tests
  - Refactor test workflow
  - Fix pip-audit dependency export
  - Enforce security scans and UTC timezone for scheduler
```

#### Группа: Рефакторинг архитектуры
```
Объединить:
* 09e8b01 refactor(core): migrate to Clean Architecture
* 8fea732 fix: resolve mypy type checking errors in repositories
* 3e6f42e fix: update tests to match refactored repository layer

В один коммит:
* refactor: migrate to Clean Architecture with repository pattern
  - Implement repository layer for data access
  - Add protocol interfaces for repositories
  - Fix mypy type checking errors
  - Update tests to use repository mocks
```

#### Группа: Исправления безопасности
```
Объединить:
* 8049f43 fix(security): add authorization checks for match and feedback handlers
* 644e6e0 fix: handle race condition in registration and prevent duplicate feedback
* 288334c fix: throttle race and rollback on dup registration
* ee3280c fix: use bot from reaction context to prevent HTTP session leak

В один коммит:
* fix(security): add authorization checks and fix race conditions
  - Add user authorization checks for match and feedback handlers
  - Handle race conditions in registration with IntegrityError
  - Prevent duplicate feedback submissions
  - Fix Redis throttling race condition
  - Use bot from context to prevent HTTP session leaks
```

#### Группа: Исправления багов
```
Объединить:
* d4542d5 fix: correct 3 bugs found by cursor review
* 8f55981 fix(helpers): prevent exception with multiple open sessions
* e4e0f83 fix(feedback): correct user ID lookup and callback prefixes
* 5eefb8b fix: handle legacy keyboard buttons and unknown callbacks
* 3e557df fix: remove legacy ReplyKeyboard buttons from previous bot
* f8f6a47 test: fix mocks for get_next_open_session after .limit(1) change

В один коммит:
* fix: resolve multiple bugs and improve error handling
  - Fix exception with multiple open sessions
  - Correct user ID lookup in feedback handlers
  - Handle legacy keyboard buttons and unknown callbacks
  - Remove legacy ReplyKeyboard buttons
  - Fix test mocks after query changes
```

#### Группа: База данных и миграции
```
Объединить:
* 461dddc db: remove redundant performance indexes
* ebd02ce chore: add postgres password env to dev compose

В один коммит:
* db: optimize database schema and configuration
  - Remove redundant indexes that duplicate unique constraints
  - Add POSTGRES_PASSWORD to development docker-compose
```

#### Группа: Улучшения кода и стиля
```
Объединить:
* e93a82d style: add explanatory comments to silent except blocks
* b81892a fix: stop reprocessing small sessions and close redis
* 57d2526 fix: remove invalid redis wait_closed call

В один коммит:
* refactor: improve code quality and resource management
  - Add explanatory comments to silent except blocks
  - Fix session reprocessing for insufficient registrations
  - Properly close Redis connections on shutdown
  - Remove invalid wait_closed() call
```

### 3. Финальная структура коммитов

```
* feat: implement Random Coffee Bot MVP
* ci: improve CI/CD pipeline and test infrastructure
* refactor: migrate to Clean Architecture with repository pattern
* fix(security): add authorization checks and fix race conditions
* fix: resolve multiple bugs and improve error handling
* db: optimize database schema and configuration
* refactor: improve code quality and resource management
* chore: add REDIS_URL configuration for Docker
```

## Инструкция по применению

### Вариант 1: Interactive Rebase (рекомендуется)

```bash
# 1. Создать резервную копию
git branch backup-develop develop

# 2. Начать интерактивный rebase с базового коммита
git rebase -i c01214b

# 3. В редакторе:
# - Объединить дублирующиеся "Alfa test MVP" коммиты (squash)
# - Переместить и объединить связанные коммиты
# - Изменить сообщения коммитов на профессиональные

# 4. После rebase (если нужно force push):
git push --force-with-lease origin develop
```

### Вариант 2: Создать новую ветку с чистой историей

```bash
# 1. Создать новую ветку от базового коммита
git checkout -b develop-clean c01214b

# 2. Создать коммиты по предложенной структуре
# (cherry-pick или создать новые коммиты)

# 3. Заменить старую ветку
git branch -D develop
git branch -m develop-clean develop
git push --force-with-lease origin develop
```

## Рекомендации по сообщениям коммитов

Использовать формат:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Типы:
- `feat`: новая функциональность
- `fix`: исправление бага
- `refactor`: рефакторинг кода
- `style`: форматирование, стиль
- `chore`: рутинные задачи
- `ci`: изменения CI/CD
- `db`: изменения БД/миграций
- `docs`: документация
- `test`: тесты

Примеры хороших сообщений:
- `feat: implement Random Coffee Bot MVP`
- `refactor: migrate to Clean Architecture with repository pattern`
- `fix(security): add authorization checks and fix race conditions`
- `ci: improve CI/CD pipeline and test infrastructure`

## Предупреждения

⚠️ **Важно**:
- Если ветка `develop` уже используется другими разработчиками, нужно согласовать изменения
- Использовать `--force-with-lease` вместо `--force` для безопасности
- Создать резервную копию перед rebase
- Убедиться, что все тесты проходят после rebase
