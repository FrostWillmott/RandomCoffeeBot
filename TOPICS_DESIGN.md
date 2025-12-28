# Дизайн тем для обсуждения

## 📋 Структура темы

```python
class Topic:
    id: int
    title: str              # "Декораторы в Python"
    description: str        # Подробное описание
    category: str           # "python_core", "frameworks", "databases", etc.
    difficulty: str         # "junior", "middle", "senior"
    questions: list[str]    # Вопросы для обсуждения
    resources: list[str]    # Ссылки на материалы
    is_active: bool
    created_at: datetime
```

## 🎯 Категории тем

### 1. Python Core (основы языка)
- Декораторы и их применение
- Генераторы vs списковые включения
- Context managers (with statement)
- Дескрипторы и property
- Метаклассы
- GIL и его влияние
- Memory management и garbage collection

### 2. Async Programming
- asyncio basics
- async/await vs threading vs multiprocessing
- Event loop internals
- Async context managers
- Async generators
- Обработка ошибок в async коде

### 3. Data Structures & Algorithms
- Реализация LRU cache
- Поиск и сортировка
- Деревья и графы
- Динамическое программирование
- Time/Space complexity анализ

### 4. Frameworks (Django/FastAPI/Flask)
- ORM vs raw SQL
- Middleware и их использование
- Background tasks
- REST API design
- Аутентификация и авторизация
- Оптимизация запросов (N+1 problem)

### 5. Databases
- Индексы и когда их использовать
- Transactions и ACID
- SQL JOIN types
- NoSQL vs SQL
- Миграции схемы БД
- Query optimization

### 6. Testing
- Unit vs Integration vs E2E
- Mocking и fixtures
- pytest best practices
- Test coverage
- TDD подход

### 7. System Design
- Масштабирование приложений
- Кэширование стратегии
- Message queues (Celery, RabbitMQ)
- Microservices vs Monolith
- Load balancing

### 8. Best Practices
- Clean Code principles
- SOLID principles
- Design patterns (Factory, Singleton, Strategy, etc.)
- Code review practices
- Рефакторинг legacy кода

### 9. DevOps для разработчика
- Docker basics
- CI/CD pipelines
- Logging и monitoring
- Deployment стратегии

### 10. Soft Skills
- Code review культура
- Работа в команде
- Планирование задач
- Техническое интервью - как проходить

---

## 💾 Источники тем

### Вариант 1: Предзаполненная база (рекомендуется для MVP)

**Плюсы:**
- Полный контроль качества
- Нет зависимости от внешних API
- Работает offline
- Предсказуемость

**Минусы:**
- Требует ручной работы
- Нужно периодически обновлять

**Реализация:**
```python
# alembic/versions/xxx_add_topics.py
def upgrade():
    topics_data = [
        {
            "title": "Декораторы в Python",
            "category": "python_core",
            "difficulty": "middle",
            "description": """
            Декораторы - мощный инструмент Python для модификации поведения функций.
            Важно понимать как они работают, когда применяются, и какие есть паттерны.
            """,
            "questions": [
                "Что такое декоратор и как он работает?",
                "Разница между @decorator и @decorator()?",
                "Как написать декоратор с параметрами?",
                "Что делает @functools.wraps?",
                "Примеры использования декораторов в production коде?"
            ],
            "resources": [
                "https://realpython.com/primer-on-python-decorators/",
                "https://peps.python.org/pep-0318/"
            ]
        },
        # ... еще ~50-100 тем
    ]

    for topic in topics_data:
        op.execute(
            topics_table.insert().values(**topic)
        )
```

**Сколько нужно тем:** Минимум 50-70 для разнообразия

---

### Вариант 2: AI-генерация (для масштабирования)

**Использование OpenAI API для генерации тем:**

```python
# app/services/ai_topic_generator.py
async def generate_topic(category: str, difficulty: str) -> dict:
    """Генерирует тему через OpenAI API"""

    prompt = f"""
    Создай тему для обсуждения на Random Coffee встрече.

    Контекст: Подготовка к собеседованию на Middle Python Developer
    Категория: {category}
    Сложность: {difficulty}

    Верни JSON:
    {{
        "title": "Краткое название темы",
        "description": "2-3 предложения описания",
        "questions": ["5 конкретных вопросов для обсуждения"],
        "resources": ["2-3 ссылки на материалы"]
    }}
    """

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
```

**Плюсы:**
- Бесконечное разнообразие
- Актуальные темы
- Можно адаптировать под конкретных участников

**Минусы:**
- Зависимость от API
- Стоимость запросов
- Нужна валидация качества
- Возможны галлюцинации

---

### Вариант 3: Комбинированный подход (оптимально)

```python
class TopicService:
    def __init__(self):
        self.manual_topics = []  # Предзаполненные
        self.ai_generated = []   # AI темы

    async def get_topic_for_match(self, match: Match) -> Topic:
        """Выбирает тему для пары"""

        # 80% времени - проверенные ручные темы
        if random.random() < 0.8:
            return await self._get_manual_topic(match)

        # 20% - AI темы для разнообразия
        else:
            return await self._get_or_generate_ai_topic(match)

    async def _get_manual_topic(self, match: Match) -> Topic:
        """Выбирает из предзаполненных тем"""
        # Исключаем темы, которые пара уже обсуждала
        used_topics = await self._get_used_topics(match.user1, match.user2)

        available = [t for t in self.manual_topics if t.id not in used_topics]

        return random.choice(available)
```

---

## 🎲 Алгоритм выбора темы

```python
async def select_topic_for_match(
    match: Match,
    user1: User,
    user2: User
) -> Topic:
    """
    Выбирает подходящую тему с учетом:
    1. Истории встреч (не повторять темы)
    2. Уровня участников
    3. Предпочтений (опционально)
    """

    # 1. Получить все темы, которые пара УЖЕ обсуждала
    discussed_topics = await get_discussed_topics(user1, user2)

    # 2. Отфильтровать доступные темы
    available_topics = await Topic.query.filter(
        Topic.id.not_in(discussed_topics),
        Topic.is_active == True,
        Topic.difficulty == "middle"  # Можно сделать динамическим
    ).all()

    # 3. Приоритизировать по категориям (если есть предпочтения)
    if user_preferences := await get_user_preferences(user1, user2):
        available_topics = prioritize_by_preferences(
            available_topics,
            user_preferences
        )

    # 4. Случайный выбор из топ-10
    top_topics = random.sample(
        available_topics,
        min(10, len(available_topics))
    )

    return random.choice(top_topics)
```

---

## 📝 Формат отправки темы паре

```
🎯 Ваша тема для обсуждения:

**Декораторы в Python**

Декораторы - мощный инструмент Python для модификации поведения функций.
Важно понимать как они работают, когда применяются, и какие есть паттерны.

💬 Вопросы для обсуждения:
1. Что такое декоратор и как он работает?
2. Разница между @decorator и @decorator()?
3. Как написать декоратор с параметрами?
4. Что делает @functools.wraps?
5. Примеры использования декораторов в production коде?

📚 Материалы:
• https://realpython.com/primer-on-python-decorators/
• https://peps.python.org/pep-0318/

Приятного обсуждения! 😊
```

---

## 🔄 Система обновления тем

### Автоматическое пополнение
```python
# app/jobs/refresh_topics.py
async def weekly_topic_refresh():
    """Еженедельное пополнение базы тем"""

    # Проверить, сколько неиспользованных тем осталось
    unused_count = await Topic.query.filter(
        Topic.times_used == 0
    ).count()

    # Если меньше 20 - добавить новые
    if unused_count < 20:
        new_topics = await generate_topics_batch(
            count=10,
            categories=["python_core", "async", "databases"]
        )

        await Topic.bulk_create(new_topics)
```

### Ручная модерация
```python
# Админ может:
# 1. Добавлять темы вручную
# 2. Редактировать существующие
# 3. Деактивировать плохие темы
# 4. Видеть статистику по темам (какие популярны)
```

---

## 📊 Метрики тем

```python
class Topic:
    # ... другие поля

    times_used: int = 0          # Сколько раз использовалась
    avg_rating: float = 0.0      # Средняя оценка от пар
    last_used_at: datetime       # Когда последний раз использовалась
```

Это позволит:
- Убирать непопулярные темы
- Балансировать частоту использования
- Улучшать качество тем на основе feedback

---

## 🎯 Рекомендация для MVP

**Начать с Варианта 1 (предзаполненная база):**

1. **Создать 50-70 качественных тем** вручную
2. **Распределить по категориям** (по 5-7 тем на категорию)
3. **Добавить через Alembic миграцию**
4. **В будущем** - добавить AI-генерацию для масштабирования

**Почему именно так:**
- ✅ Быстрый старт без зависимостей
- ✅ Гарантированное качество
- ✅ Нет расходов на API
- ✅ Можно итеративно улучшать

**Могу помочь составить список из 50 тем прямо сейчас?** 📝
