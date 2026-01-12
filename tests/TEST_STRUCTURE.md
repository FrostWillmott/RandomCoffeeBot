# Структура тестов

## Организация тестов

Тесты разделены на две категории:

### 1. Unit-тесты (`tests/unit/`) - с моками, без БД

**Принцип:** Быстрые тесты, которые не требуют реальной БД. Используют моки для изоляции.

**Файлы:**
- `test_announcements_mocked.py` - тесты для announcements service
- `test_config.py` - тесты для конфигурации
- `test_db_session.py` - тесты для работы с сессиями БД
- `test_helpers_mocked.py` - тесты для helpers service
- `test_matching_functions.py` - тесты для matching service
- `test_notifications_mocked.py` - тесты для notifications service
- `test_reactions_handler.py` - тесты для обработки реакций
- `test_scheduler.py` - тесты для планировщика задач
- `test_schemas_callbacks.py` - тесты для схем callback данных
- `test_sessions_mocked.py` - тесты для sessions service
- `test_utils_context.py` - тесты для утилит контекста
- `test_utils_retry.py` - тесты для утилит retry логики

**Итого:** ~82 unit-теста

**Преимущества:**
- Быстрые (не требуют БД)
- Изолированные (не зависят от внешних ресурсов)
- Легко запускать локально

### 2. Интеграционные тесты (`tests/integration/`) - с реальной БД

**Принцип:** Тесты, которые проверяют реальную интеграцию с БД и сложную бизнес-логику.

**Файлы:**
- `test_e2e_flow.py` - end-to-end тесты полного потока регистрации и матчинга
- `test_helpers.py` - интеграционные тесты для helpers service
- `test_matching.py` - интеграционные тесты для matching алгоритма
- `test_sessions.py` - интеграционные тесты для sessions service

**Итого:** ~18 интеграционных тестов

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

Текущее покрытие: **81%+** (весь проект)

- Models: 100%
- Services: 73-85%
  - announcements: 84%
  - helpers: 100%
  - sessions: 86%
  - notifications: 78%
  - matching: 73% (сложная логика, требует интеграционных тестов)
- Repositories: 70-94%
- Utils: 65-100%
