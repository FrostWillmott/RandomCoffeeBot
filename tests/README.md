# Тестирование

## Конфигурация тестовой базы данных

Тесты используют **отдельный контейнер PostgreSQL** для полной изоляции от продакшн данных.

### Изоляция тестов

1. **Отдельный контейнер:** `randomcoffee-db-test` на порту 5434
2. **Отдельная БД:** `randomcoffee_test` (изолирована от продакшн)
3. **Транзакционная изоляция:** Каждый тест запускается в отдельной транзакции, которая автоматически откатывается после завершения
4. **Автоматическая очистка:** Данные не накапливаются между тестами
5. **In-memory хранилище:** Используется tmpfs для скорости

### Быстрый старт

#### Использование Makefile (рекомендуется)

```bash
# Запустить тесты (автоматически запустит/остановит тестовую БД)
make test

# Запустить тесты с покрытием
make test-coverage

# Запустить тесты в watch mode
make test-watch
```

#### Ручное управление

```bash
# Запустить тестовую БД
make test-db-up
# или
docker-compose -f docker-compose.test.yml up -d db-test

# Запустить тесты
uv run pytest tests/ -v

# Остановить тестовую БД
make test-db-down
# или
docker-compose -f docker-compose.test.yml down
```

### Настройка

#### Переменные окружения

- `TEST_DATABASE_NAME` - имя тестовой БД (по умолчанию: `randomcoffee_test`)
- `TEST_DATABASE_HOST` - хост БД (по умолчанию: `localhost`)
- `TEST_DATABASE_PORT` - порт БД (по умолчанию: `5434` - отдельно от продакшн на 5432)
- `TEST_DATABASE_USER` - пользователь БД (по умолчанию: `postgres`)
- `TEST_DATABASE_PASSWORD` - пароль БД (по умолчанию: `postgres`)
- `TEST_DATABASE_URL` - полный URL тестовой БД (переопределяет все выше)
- `TEST_DATABASE_BASE_URL` - URL для подключения к postgres БД (для создания тестовой БД)

### Запуск тестов

```bash
# Все тесты (с автоматическим управлением БД)
make test

# Все тесты (если БД уже запущена)
uv run pytest tests/ -v

# Только unit-тесты
uv run pytest tests/unit/ -v

# Только интеграционные тесты
uv run pytest tests/integration/ -v

# С покрытием кода
make test-coverage
# или
uv run pytest tests/ --cov=app --cov-report=html
```

### Структура тестов

```
tests/
├── conftest.py                    # Конфигурация и фикстуры
├── unit/                           # Unit-тесты (~82 теста)
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
└── integration/                    # Интеграционные тесты (~18 тестов)
    ├── test_e2e_flow.py
    ├── test_helpers.py
    ├── test_matching.py
    └── test_sessions.py
```

### Важные моменты

1. **Изоляция:** Каждый тест изолирован через транзакции
2. **Автоматическая очистка:** Не нужно вручную удалять данные
3. **Быстрота:** Транзакции быстрее чем полная очистка БД
4. **Безопасность:** Продакшн БД никогда не используется для тестов

### Преимущества текущей конфигурации

1. **Полная изоляция:** Отдельный контейнер, отдельный порт, отдельная БД
2. **Быстрота:** tmpfs для in-memory хранилища
3. **Автоматизация:** Makefile команды для удобства
4. **Безопасность:** Продакшн БД никогда не используется
5. **Параллельность:** Можно запускать тесты параллельно с продакшн

### Troubleshooting

**Ошибка подключения к БД:**
```bash
# Проверить, что тестовая БД запущена
docker-compose -f docker-compose.test.yml ps

# Проверить логи
docker-compose -f docker-compose.test.yml logs db-test

# Проверить подключение
psql -h localhost -p 5434 -U postgres -d randomcoffee_test
```

**Конфликт портов:**
- Убедитесь, что порт 5434 свободен
- Или измените `TEST_DATABASE_PORT` в переменных окружения

**Тесты не изолированы:**
- Убедитесь, что используется фикстура `db_session`
- Проверьте, что транзакции откатываются (см. `conftest.py`)
- Убедитесь, что используется правильный порт (5434, а не 5432)
