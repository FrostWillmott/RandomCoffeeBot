# Руководство по тестированию Random Coffee Bot

Это руководство поможет вам проверить работоспособность бота и убедиться, что все функции работают корректно.

## Раздел 1: Подготовка

### 1.1 Проверка конфигурации

Убедитесь, что файл `.env` настроен правильно:

```bash
# Проверьте наличие обязательных переменных:
TELEGRAM_BOT_TOKEN=your_bot_token_here
CHANNEL_ID=@your_channel_username
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/randomcoffee
REDIS_URL=redis://redis:6379/0
```

**Важно:**
- `TELEGRAM_BOT_TOKEN` должен быть получен от [@BotFather](https://t.me/BotFather)
- `CHANNEL_ID` должен быть ID или username канала, где будут публиковаться анонсы
- Для локального запуска измените `DATABASE_URL` на `postgresql+asyncpg://postgres:postgres@localhost:5432/randomcoffee`

### 1.2 Проверка миграций базы данных

Убедитесь, что все миграции применены:

```bash
# В Docker:
make migrate

# Локально:
alembic upgrade head
```

### 1.3 Проверка наличия тем в базе данных

Темы для обсуждения должны быть загружены в базу данных. Проверьте и загрузите при необходимости:

```bash
# В Docker:
make db-seed

# Локально:
uv run python scripts/seed_topics.py
```

Скрипт автоматически проверит наличие тем и загрузит их, если база пуста.

**Проверка через SQL (опционально):**

```bash
# Подключиться к базе данных:
make db-shell

# Выполнить запрос:
SELECT COUNT(*) FROM topics WHERE is_active = true;
SELECT category, COUNT(*) FROM topics GROUP BY category;
```

Должно быть загружено несколько десятков тем по различным категориям (core_python, frameworks, architecture, etc.).

## Раздел 2: Запуск бота

### 2.1 Запуск в Docker (рекомендуется)

```bash
# Запустить все сервисы (bot, db, redis):
make dev

# Проверить статус контейнеров:
make ps

# Просмотреть логи:
make logs

# Или логи только бота:
docker compose logs -f bot
```

**Проверка успешного запуска:**

1. В логах должно быть сообщение о запуске бота:
   ```
   Bot started successfully
   Scheduler started
   ```

2. Контейнеры должны быть в статусе `Up`:
   ```bash
   make ps
   ```

3. Проверьте healthcheck файл (если настроен):
   ```bash
   docker compose exec bot cat /tmp/healthy
   ```

### 2.2 Запуск локально (без Docker)

**Требования:**
- PostgreSQL должен быть запущен на localhost:5432
- Redis должен быть запущен на localhost:6379
- В `.env` изменен `DATABASE_URL` на `postgresql+asyncpg://postgres:postgres@localhost:5432/randomcoffee`

```bash
# Запустить бота:
make run

# Или напрямую:
uv run python -m app.main
```

**Проверка успешного запуска:**

В консоли должны появиться сообщения:
```
INFO: Bot started successfully
INFO: Scheduler started
INFO: Polling started
```

## Раздел 3: Тестирование основных функций

### 3.1 Тестирование команды /start

1. Найдите вашего бота в Telegram (по username, который вы указали при создании)
2. Отправьте команду `/start`
3. **Ожидаемый результат:**
   - Бот должен ответить приветственным сообщением
   - Должно появиться главное меню с кнопками
   - Для новых пользователей: полное описание работы бота
   - Для существующих: краткое приветствие

**Проверка в базе данных:**
```bash
make db-shell
SELECT * FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;
```

Пользователь должен быть создан или обновлен в базе данных.

### 3.2 Тестирование команды /help

1. Отправьте команду `/help` боту
2. **Ожидаемый результат:**
   - Бот должен отправить сообщение со справкой
   - Должна быть информация о доступных командах
   - Должно быть описание процесса Random Coffee

### 3.3 Тестирование команды /status

1. Отправьте команду `/status` боту
2. **Ожидаемый результат:**
   - Бот должен показать ваш текущий статус
   - Информацию о регистрациях на предстоящие сессии
   - Информацию о текущих матчах

### 3.4 Тестирование главного меню

1. Нажмите на кнопки в главном меню:
   - **"Регистрация"** - должна открыться форма регистрации
   - **"Мои матчи"** - должны показаться ваши текущие матчи
   - **"Справка"** - должна показаться справка

### 3.5 Тестирование работы планировщика

Планировщик автоматически выполняет задачи по расписанию. Для тестирования можно запустить задачи вручную:

#### 3.5.1 Создание сессии

```bash
# В Docker:
docker compose exec bot python -m scripts.test_run create_session

# Локально:
uv run python -m scripts.test_run create_session
```

**Ожидаемый результат:**
- В логах должно быть сообщение о создании сессии
- В канале (указанном в `CHANNEL_ID`) должно появиться сообщение-анонс
- В базе данных должна быть создана новая сессия:
  ```bash
  make db-shell
  SELECT * FROM sessions ORDER BY created_at DESC LIMIT 1;
  ```

#### 3.5.2 Закрытие регистраций

```bash
# В Docker:
docker compose exec bot python -m scripts.test_run close_registrations

# Локально:
uv run python -m scripts.test_run close_registrations
```

**Ожидаемый результат:**
- Сессии с истекшим сроком регистрации должны быть закрыты
- Статус сессий должен измениться на `CLOSED`

#### 3.5.3 Запуск матчинга

**Важно:** Матчинг работает только для сессий со статусом `CLOSED` и истекшим дедлайном регистрации. Если сессия еще открыта, матчинг не найдет сессий для обработки.

**Подготовка сессии к матчингу:**

Перед запуском матчинга нужно убедиться, что сессия закрыта. Есть два способа:

**Способ 1: Автоматическое закрытие (рекомендуется для тестирования)**
```bash
# Установить дедлайн на прошедшую дату
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

# Закрыть регистрации (автоматически закроет сессию)
docker compose exec bot python -m scripts.test_run close_registrations
```

**Способ 2: Ручное закрытие**
```bash
# ВАЖНО: При ручном закрытии также нужно установить прошедший дедлайн,
# иначе матчинг не найдет сессию (требуется: status = 'closed' AND registration_deadline < NOW())

# Установить прошедший дедлайн
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

# Закрыть сессию вручную
docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET status = 'closed' WHERE id = SESSION_ID;"
```

**Запуск матчинга:**
```bash
# В Docker:
docker compose exec bot python -m scripts.test_run run_matching

# Локально:
uv run python -m scripts.test_run run_matching
```

**Ожидаемый результат:**
- Для закрытых сессий должны быть созданы матчи
- Участники должны получить уведомления о матчах в канале и личные сообщения
- В базе данных должны быть созданы записи в таблице `matches`

**Проверка в базе данных:**
```bash
make db-shell
SELECT * FROM matches ORDER BY created_at DESC LIMIT 5;
SELECT * FROM registrations WHERE session_id = SESSION_ID;
SELECT id, status, registration_deadline FROM sessions WHERE id = SESSION_ID;
```

**Если матчинг не находит сессий:**
- Убедитесь, что сессия имеет статус `CLOSED`
- **КРИТИЧНО:** Проверьте, что `registration_deadline < NOW()` - матчинг требует ОБА условия:
  - `status = 'closed'` И
  - `registration_deadline < current_time`
- Если дедлайн в будущем, установите прошедшую дату:
  ```bash
  docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"
  ```
- Проверьте наличие регистраций на сессию (минимум 2 пользователя для пары, 3 для триплета)

#### 3.5.4 Запуск всех задач

```bash
# В Docker:
docker compose exec bot python -m scripts.test_run all

# Локально:
uv run python -m scripts.test_run all
```

Это выполнит все три задачи последовательно.

### 3.6 Тестирование полного цикла

1. **Создайте тестовую сессию:**
   ```bash
   docker compose exec bot python -m scripts.test_run create_session
   ```

2. **Зарегистрируйтесь через бота:**
   - Откройте канал, где был опубликован анонс
   - Поставьте реакцию 👍 на сообщение-анонс
   - Или используйте команду регистрации в боте

3. **Проверьте регистрацию:**
   ```bash
   make db-shell
   SELECT * FROM registrations WHERE user_id = YOUR_USER_ID;
   ```

4. **Подготовьте сессию к матчингу:**

   **Вариант A: Автоматическое закрытие (рекомендуется)**
   ```bash
   # Установить дедлайн на прошедшую дату
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

   # Закрыть регистрации (автоматически закроет сессию)
   docker compose exec bot python -m scripts.test_run close_registrations
   ```

   **Вариант B: Ручное закрытие**
   ```bash
   # ВАЖНО: При ручном закрытии также нужно установить прошедший дедлайн,
   # иначе матчинг не найдет сессию

   # Установить прошедший дедлайн
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"

   # Закрыть сессию вручную
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET status = 'closed' WHERE id = SESSION_ID;"
   ```

5. **Запустите матчинг:**
   ```bash
   docker compose exec bot python -m scripts.test_run run_matching
   ```

6. **Проверьте результат:**
   - В канале должно появиться сообщение со списком всех матчей
   - Вы должны получить личное уведомление о матче
   - В базе данных должен быть создан матч с темой для обсуждения
   ```bash
   make db-shell
   SELECT m.id, u1.username as user1, u2.username as user2, t.title as topic
   FROM matches m
   JOIN users u1 ON m.user1_id = u1.id
   JOIN users u2 ON m.user2_id = u2.id
   LEFT JOIN topics t ON m.topic_id = t.id
   WHERE m.session_id = SESSION_ID;
   ```

## Раздел 4: Проверка работоспособности

### 4.1 Проверка подключения к базе данных

```bash
# Проверить подключение через psql:
make db-shell

# Или проверить через Python:
docker compose exec bot python -c "
from app.db.session import engine
import asyncio
async def check():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT 1')
        print('Database connection: OK')
asyncio.run(check())
"
```

**Ожидаемый результат:** Подключение успешно, запрос выполняется.

### 4.2 Проверка подключения к Telegram API

```bash
# Проверить через логи:
make logs | grep -i "telegram\|bot started"

# Или проверить статус бота:
docker compose exec bot python -c "
from app.bot import get_bot
import asyncio
async def check():
    bot = get_bot()
    me = await bot.get_me()
    print(f'Bot connected: {me.username} (@{me.username})')
asyncio.run(check())
"
```

**Ожидаемый результат:** Бот успешно подключен, возвращается информация о боте.

### 4.3 Проверка работы Redis

```bash
# Проверить подключение к Redis:
docker compose exec redis redis-cli ping

# Должно вернуться: PONG
```

### 4.4 Проверка логов на ошибки

```bash
# Просмотреть логи:
make logs

# Или только ошибки:
make logs | grep -i "error\|exception\|failed"

# Проверить логи бота:
docker compose logs bot | tail -50
```

**Что проверить:**
- Нет критических ошибок (ERROR, CRITICAL)
- Нет исключений (Exception, Traceback)
- Нет проблем с подключением к БД или Telegram API

## Раздел 5: Типичные проблемы и решения

### 5.1 Бот не отвечает на команды

**Возможные причины:**
1. Бот не запущен - проверьте `make ps` или логи
2. Неверный `TELEGRAM_BOT_TOKEN` - проверьте `.env` файл
3. Бот заблокирован пользователем - разблокируйте бота в Telegram

**Решение:**
```bash
# Проверить статус:
make ps

# Перезапустить:
make down
make dev

# Проверить логи:
make logs
```

### 5.2 Ошибки подключения к базе данных

**Возможные причины:**
1. База данных не запущена
2. Неверный `DATABASE_URL` в `.env`
3. Миграции не применены

**Решение:**
```bash
# Проверить статус БД:
docker compose ps db

# Проверить подключение:
make db-shell

# Применить миграции:
make migrate

# Перезапустить БД:
docker compose restart db
```

### 5.3 Отсутствие тем в базе данных

**Признаки:**
- При матчинге нет доступных тем
- В логах: "No topics available for matching!"

**Решение:**
```bash
# Загрузить темы:
make db-seed

# Проверить количество:
make db-shell
SELECT COUNT(*) FROM topics WHERE is_active = true;
```

### 5.4 Проблемы с конфигурацией

**Признаки:**
- Ошибки при запуске бота
- Сообщения о недостающих переменных окружения

**Решение:**
1. Проверьте наличие файла `.env`
2. Убедитесь, что все обязательные переменные установлены:
   - `TELEGRAM_BOT_TOKEN`
   - `CHANNEL_ID`
   - `DATABASE_URL`
   - `REDIS_URL`
3. Проверьте формат значений (без лишних пробелов, кавычек)
4. Перезапустите бота после изменения `.env`:
   ```bash
   make down
   make dev
   ```

### 5.5 Планировщик не выполняет задачи

**Признаки:**
- Сессии не создаются автоматически
- Регистрации не закрываются
- Матчинг не запускается

**Решение:**
1. Проверьте логи планировщика:
   ```bash
   make logs | grep -i "scheduler\|job"
   ```

2. Запустите задачи вручную для проверки:
   ```bash
   docker compose exec bot python -m scripts.test_run all
   ```

3. Проверьте настройки планировщика в `app/scheduler.py` и `app/constants.py`

### 5.7 Матчинг не находит сессий для обработки

**Признаки:**
- Команда `run_matching` завершается без ошибок, но сообщает "0 sessions"
- В логах: "Closed registration for 0 sessions" или "Found 0 closed sessions ready for matching"

**Возможные причины:**
1. Сессия еще открыта (статус `open` вместо `closed`)
2. Дедлайн регистрации еще не истек
3. Нет регистраций на сессию

**Решение:**
1. Проверьте статус сессии:
   ```bash
   make db-shell
   SELECT id, status, registration_deadline, NOW() as current_time FROM sessions WHERE id = SESSION_ID;
   ```

2. Если сессия открыта, закройте ее:
   ```bash
   # Установить прошедший дедлайн и закрыть автоматически
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"
   docker compose exec bot python -m scripts.test_run close_registrations

   # Или закрыть вручную (ВАЖНО: также установить прошедший дедлайн!)
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET registration_deadline = NOW() - INTERVAL '1 day' WHERE id = SESSION_ID;"
   docker compose exec -T db psql -U randomcoffee -d randomcoffee -c "UPDATE sessions SET status = 'closed' WHERE id = SESSION_ID;"
   ```

3. Проверьте наличие регистраций:
   ```bash
   make db-shell
   SELECT COUNT(*) FROM registrations WHERE session_id = SESSION_ID;
   ```
   Должно быть минимум 2 регистрации для создания пары.

### 5.6 Уведомления не отправляются

**Возможные причины:**
1. Пользователь заблокировал бота
2. Ошибки в Telegram API
3. Неверный формат сообщений

**Решение:**
1. Проверьте логи на ошибки отправки:
   ```bash
   make logs | grep -i "notification\|telegram\|send"
   ```

2. Проверьте, что пользователь не заблокировал бота
3. Проверьте права бота (должен иметь возможность отправлять сообщения)

## Чеклист быстрой проверки

Используйте этот чеклист для быстрой проверки работоспособности:

- [ ] Конфигурация `.env` настроена правильно
- [ ] Миграции применены (`make migrate`)
- [ ] Темы загружены в БД (`make db-seed`)
- [ ] Бот запущен и работает (`make ps`, `make logs`)
- [ ] Команда `/start` работает и создает пользователя
- [ ] Команда `/help` возвращает справку
- [ ] Команда `/status` показывает статус пользователя
- [ ] Главное меню отображается корректно
- [ ] Создание сессии работает (`scripts/test_run create_session`)
- [ ] Анонс публикуется в канале
- [ ] Регистрация через реакцию работает
- [ ] Сессия закрыта перед запуском матчинга (статус `closed`, дедлайн истек)
- [ ] Матчинг создает пары (`scripts/test_run run_matching`)
- [ ] Уведомления о матчах отправляются
- [ ] Нет ошибок в логах

## Дополнительные команды для отладки

```bash
# Просмотр всех пользователей:
make db-shell
SELECT id, telegram_id, username, first_name, is_active FROM users;

# Просмотр всех сессий:
SELECT id, date, status, registration_deadline FROM sessions ORDER BY date DESC;

# Просмотр всех регистраций:
SELECT r.id, u.username, s.date, r.created_at
FROM registrations r
JOIN users u ON r.user_id = u.id
JOIN sessions s ON r.session_id = s.id
ORDER BY r.created_at DESC;

# Просмотр всех матчей:
SELECT m.id, u1.username as user1, u2.username as user2, t.title as topic, m.status
FROM matches m
JOIN users u1 ON m.user1_id = u1.id
JOIN users u2 ON m.user2_id = u2.id
LEFT JOIN topics t ON m.topic_id = t.id
ORDER BY m.created_at DESC;

# Очистка тестовых данных (осторожно!):
# Удалить все регистрации и матчи для тестирования:
DELETE FROM matches;
DELETE FROM registrations;
```

---

**Примечание:** При тестировании в продакшн-окружении будьте осторожны с удалением данных и запуском тестовых команд.
