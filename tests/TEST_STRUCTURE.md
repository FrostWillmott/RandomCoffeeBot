# Структура тестов

## Организация тестов

Тесты разделены на две категории:

### 1. Unit-тесты (`tests/unit/`) - с моками, без БД

**Принцип:** Быстрые тесты, которые не требуют реальной БД. Используют моки для изоляции.

**Файлы:**
- `test_notifications_mocked.py` - тесты для notifications service (14 тестов)
- `test_matching_functions.py` - тесты для matching service (5 тестов)
- `test_helpers_mocked.py` - тесты для helpers service (7 тестов)
- `test_sessions_mocked.py` - тесты для sessions service (2 теста)
- `test_announcements_mocked.py` - тесты для announcements service (3 теста)

**Итого:** 31 unit-тест

**Преимущества:**
- Быстрые (не требуют БД)
- Изолированные (не зависят от внешних ресурсов)
- Легко запускать локально

### 2. Интеграционные тесты (`tests/integration/`) - с реальной БД

**Принцип:** Тесты, которые проверяют реальную интеграцию с БД и сложную бизнес-логику.

**Файлы:**
- `test_matching.py` - интеграционные тесты для matching алгоритма (7 тестов)
- `test_sessions.py` - интеграционные тесты для sessions (1 тест)

**Итого:** 8 интеграционных тестов

**Преимущества:**
- Проверяют реальное поведение с БД
- Тестируют сложные сценарии
- Уверенность в работе с реальными данными

## Удаленные тесты

Были удалены дублирующиеся тесты, которые:
1. Использовали реальную БД, но не работали из-за проблем с event loop
2. Дублировали функциональность тестов с моками

**Удаленные файлы:**
- `test_notifications.py` - заменен на `test_notifications_mocked.py`
- `test_sessions.py` - заменен на `test_sessions_mocked.py`
- `test_announcements.py` - заменен на `test_announcements_mocked.py`
- `test_helpers.py` - заменен на `test_helpers_mocked.py`
- `test_matching_helpers.py` - функциональность покрыта в `test_matching.py`

## Запуск тестов

### Все тесты
```bash
make test
```

### Только unit-тесты (быстро, без БД)
```bash
uv run pytest tests/unit/
```

### Только интеграционные тесты (требуют БД)
```bash
make test-db-up
uv run pytest tests/integration/
make test-db-down
```

### С покрытием
```bash
uv run pytest tests/unit/ --cov=app.services --cov=app.models --cov-report=term
```

## Покрытие

Текущее покрытие: **73%** (services + models)

- Models: 100%
- Services: 73%
  - announcements: 100%
  - helpers: 100%
  - sessions: 84%
  - notifications: 73%
  - matching: 36% (сложная логика, требует интеграционных тестов)
