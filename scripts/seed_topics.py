"""Заполнение базы данных темами для интервью Python Middle."""

import asyncio
from datetime import UTC, datetime

from sqlalchemy import func, select

from app.db.session import async_session_maker
from app.models.topic import Topic

TOPICS = [
    {
        "title": "Декораторы и замыкания",
        "description": "Понимание декораторов Python, замыканий и их"
        " практического применения",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Что такое замыкание и как оно работает?",
            "Как декораторы работают внутри?",
            "В чем разница между декораторами классов и функций?",
            "Как создать декоратор с аргументами?",
        ],
        "resources": [
            "https://habr.com/ru/companies/otus/articles/461087/",
            "https://docs.python.org/3/glossary.html#term-decorator",
        ],
    },
    {
        "title": "Менеджеры контекста",
        "description": "Глубокое погружение в менеджеры контекста и оператор with",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Что такое менеджер контекста?",
            "Как работают методы __enter__ и __exit__?",
            "Когда стоит использовать contextlib.contextmanager?",
            "Как менеджеры контекста помогают в управлении ресурсами?",
        ],
        "resources": [
            "https://docs.python.org/3/library/contextlib.html",
            "https://habr.com/ru/articles/196382/",
        ],
    },
    {
        "title": "Генераторы и итераторы",
        "description": "Понимание генераторов, итераторов и ленивых вычислений",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "В чем разница между итератором и итерируемым объектом?",
            "Как работают генераторы? Что такое yield?",
            "Выражения-генераторы против списковых включений (list comprehensions)?",
            "Когда стоит использовать модуль itertools?",
        ],
        "resources": [
            "https://habr.com/ru/articles/488112/",
            "https://docs.python.org/3/library/itertools.html",
        ],
    },
    {
        "title": "Метаклассы и дескрипторы",
        "description": "Продвинутый Python: метаклассы, дескрипторы и объектная модель",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Что такое метакласс?",
            "Как работают дескрипторы (__get__, __set__, __delete__)?",
            "В чем разница между __new__ и __init__?",
            "Как работает поиск атрибутов в Python?",
        ],
        "resources": [
            "https://habr.com/ru/articles/145835/",
            "https://docs.python.org/3/howto/descriptor.html",
        ],
    },
    {
        "title": "Управление памятью и GC",
        "description": "Понимание модели памяти Python и сборки мусора",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Как Python управляет памятью?",
            "Что такое подсчет ссылок?",
            "Как работает сборщик мусора (GC)?",
            "Что такое циклические ссылки и как они обрабатываются?",
        ],
        "resources": [
            "https://habr.com/ru/articles/417559/",
            "https://docs.python.org/3/library/gc.html",
        ],
    },
    {
        "title": "GIL и многопоточность",
        "description": "Global Interpreter Lock and its implications",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Что такое GIL?",
            "How does the GIL affect multithreading?",
            "When should you use threading vs multiprocessing?",
            "How do asyncio and threading differ?",
        ],
        "resources": [
            "https://habr.com/ru/articles/84629/",
            "https://docs.python.org/3/library/threading.html",
        ],
    },
    {
        "title": "Type hints и mypy",
        "description": "Статическая типизация в Python с использованием подсказок типов",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Что такое type hints и зачем они нужны?",
            "Как работает mypy?",
            "Что такое Generic типы?",
            "Как типизировать декораторы и функции высшего порядка?",
        ],
        "resources": [
            "https://habr.com/ru/articles/346542/",
            "https://mypy.readthedocs.io/",
        ],
    },
    {
        "title": "Data classes и attrs",
        "description": "Modern approaches to creating classes in Python",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What are dataclasses and when to use them?",
            "How do attrs compare to dataclasses?",
            "What is __post_init__?",
            "How do you handle immutability?",
        ],
        "resources": [
            "https://habr.com/ru/articles/415829/",
            "https://www.attrs.org/",
        ],
    },
    {
        "title": "Protocol и ABC",
        "description": "Abstract base classes vs protocols for polymorphism",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What's the difference between ABC and Protocol?",
            "When should you use duck typing vs nominal typing?",
            "How do you create an abstract base class?",
            "What is structural subtyping?",
        ],
        "resources": [
            "https://peps.python.org/pep-0544/",
            "https://docs.python.org/3/library/abc.html",
        ],
    },
    {
        "title": "Внутреннее устройство Python",
        "description": "How Python works under the hood",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "How does Python execute code?",
            "What is bytecode?",
            "How do dictionaries work internally?",
            "What are slots and when to use them?",
        ],
        "resources": [
            "https://habr.com/ru/articles/430338/",
            "https://docs.python.org/3/library/dis.html",
        ],
    },
    {
        "title": "Основы Asyncio",
        "description": "Understanding async/await and the event loop",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "What is an event loop?",
            "How do async/await work?",
            "What's the difference between coroutine and task?",
            "When should you use asyncio?",
        ],
        "resources": [
            "https://habr.com/ru/articles/337420/",
            "https://docs.python.org/3/library/asyncio.html",
        ],
    },
    {
        "title": "Паттерны Asyncio",
        "description": "Common patterns in asyncio programming",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "How do you handle timeouts in async code?",
            "What is gather vs wait?",
            "How do you handle errors in async tasks?",
            "What are async context managers?",
        ],
        "resources": [
            "https://docs.python.org/3/library/asyncio-task.html",
            "https://habr.com/ru/articles/667630/",
        ],
    },
    {
        "title": "Асинхронные библиотеки",
        "description": "Popular async libraries: aiohttp, httpx, asyncpg",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "How does aiohttp work?",
            "What are the differences between aiohttp and httpx?",
            "How do you use asyncpg?",
            "What is connection pooling in async?",
        ],
        "resources": [
            "https://docs.aiohttp.org/",
            "https://www.python-httpx.org/",
        ],
    },
    {
        "title": "Async против Threading",
        "description": "Choosing between async and threading",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "When to use asyncio vs threading?",
            "What is I/O-bound vs CPU-bound?",
            "How do you run blocking code in async?",
            "What is run_in_executor?",
        ],
        "resources": [
            "https://habr.com/ru/articles/437354/",
            "https://docs.python.org/3/library/asyncio-eventloop.html",
        ],
    },
    {
        "title": "Асинхронные генераторы",
        "description": "Asynchronous iteration and generators",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "What is an async generator?",
            "How do async for loops work?",
            "What is __aiter__ and __anext__?",
            "When would you use async comprehensions?",
        ],
        "resources": [
            "https://peps.python.org/pep-0525/",
            "https://docs.python.org/3/reference/expressions.html#asynchronous-generator-functions",
        ],
    },
    {
        "title": "Отладка Asyncio",
        "description": "Debugging and profiling async code",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "How do you debug async code?",
            "What tools exist for async profiling?",
            "How do you detect blocking calls?",
            "What is asyncio debug mode?",
        ],
        "resources": [
            "https://docs.python.org/3/library/asyncio-dev.html",
            "https://habr.com/ru/articles/667630/",
        ],
    },
    {
        "title": "Тестирование асинхронного кода",
        "description": "Testing asynchronous code",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "How do you test async functions?",
            "What is pytest-asyncio?",
            "How do you mock async functions?",
            "What are async fixtures?",
        ],
        "resources": [
            "https://pytest-asyncio.readthedocs.io/",
            "https://habr.com/ru/articles/671752/",
        ],
    },
    {
        "title": "Основы FastAPI",
        "description": "Building APIs with FastAPI",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "How does FastAPI dependency injection work?",
            "What is Pydantic validation?",
            "How do you handle authentication in FastAPI?",
            "What are path operations and dependencies?",
        ],
        "resources": [
            "https://fastapi.tiangolo.com/",
            "https://habr.com/ru/articles/513310/",
        ],
    },
    {
        "title": "Проектирование REST API",
        "description": "Best practices for REST API design",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "What are REST principles?",
            "How do you version APIs?",
            "What is HATEOAS?",
            "How do you handle pagination and filtering?",
        ],
        "resources": [
            "https://restfulapi.net/",
            "https://habr.com/ru/articles/483202/",
        ],
    },
    {
        "title": "Django ORM",
        "description": "Working with Django's object-relational mapper",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "How does Django ORM work?",
            "What is N+1 query problem?",
            "How do select_related and prefetch_related work?",
            "What are Django signals?",
        ],
        "resources": [
            "https://docs.djangoproject.com/en/stable/topics/db/",
            "https://habr.com/ru/articles/475148/",
        ],
    },
    {
        "title": "Аутентификация и авторизация",
        "description": "Implementing auth in web applications",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "What's the difference between authentication and authorization?",
            "How does JWT work?",
            "What is OAuth2?",
            "How do you implement role-based access control?",
        ],
        "resources": [
            "https://habr.com/ru/articles/340146/",
            "https://fastapi.tiangolo.com/tutorial/security/",
        ],
    },
    {
        "title": "Middleware и CORS",
        "description": "Understanding middleware and CORS in web apps",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "What is middleware?",
            "How does CORS work?",
            "What are preflight requests?",
            "How do you implement custom middleware?",
        ],
        "resources": [
            "https://fastapi.tiangolo.com/tutorial/middleware/",
            "https://developer.mozilla.org/ru/docs/Web/HTTP/CORS",
        ],
    },
    {
        "title": "WebSockets",
        "description": "Real-time communication with WebSockets",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "How do WebSockets work?",
            "What's the difference between WebSockets and HTTP?",
            "How do you implement WebSockets in FastAPI?",
            "What are connection lifecycle events?",
        ],
        "resources": [
            "https://fastapi.tiangolo.com/advanced/websockets/",
            "https://habr.com/ru/articles/513310/",
        ],
    },
    {
        "title": "Документирование API",
        "description": "Generating and maintaining API documentation",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "What is OpenAPI/Swagger?",
            "How does FastAPI generate docs?",
            "What is the difference between Swagger and ReDoc?",
            "How do you customize API documentation?",
        ],
        "resources": [
            "https://swagger.io/specification/",
            "https://fastapi.tiangolo.com/tutorial/metadata/",
        ],
    },
    {
        "title": "Валидация запросов",
        "description": "Input validation and error handling",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "How does Pydantic validation work?",
            "What are custom validators?",
            "How do you handle validation errors?",
            "What is the difference between response_model and return type?",
        ],
        "resources": [
            "https://pydantic-docs.helpmanual.io/",
            "https://fastapi.tiangolo.com/tutorial/response-model/",
        ],
    },
    {
        "title": "SQLAlchemy Core против ORM",
        "description": "Understanding SQLAlchemy architecture",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "What's the difference between Core and ORM?",
            "When should you use Core vs ORM?",
            "How do you build complex queries?",
            "What is the unit of work pattern?",
        ],
        "resources": [
            "https://docs.sqlalchemy.org/en/20/",
            "https://habr.com/ru/articles/556314/",
        ],
    },
    {
        "title": "Транзакции базы данных",
        "description": "ACID properties and transaction management",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "What are ACID properties?",
            "How do transactions work in PostgreSQL?",
            "What is optimistic vs pessimistic locking?",
            "How do you handle deadlocks?",
        ],
        "resources": [
            "https://www.postgresql.org/docs/current/tutorial-transactions.html",
            "https://habr.com/ru/articles/463669/",
        ],
    },
    {
        "title": "Оптимизация запросов",
        "description": "Optimizing database queries and indexes",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "How do indexes work?",
            "What is EXPLAIN ANALYZE?",
            "How do you identify slow queries?",
            "What are composite indexes?",
        ],
        "resources": [
            "https://www.postgresql.org/docs/current/performance-tips.html",
            "https://habr.com/ru/articles/276633/",
        ],
    },
    {
        "title": "Миграции базы данных",
        "description": "Managing schema changes with Alembic",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "What are database migrations?",
            "How does Alembic work?",
            "How do you handle migration conflicts?",
            "What is the difference between upgrade and downgrade?",
        ],
        "resources": [
            "https://alembic.sqlalchemy.org/",
            "https://habr.com/ru/articles/510444/",
        ],
    },
    {
        "title": "Пул соединений",
        "description": "Managing database connections efficiently",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "What is connection pooling?",
            "How does SQLAlchemy's pool work?",
            "What are pool size and max overflow?",
            "How do you handle connection timeouts?",
        ],
        "resources": [
            "https://docs.sqlalchemy.org/en/20/core/pooling.html",
            "https://habr.com/ru/articles/333162/",
        ],
    },
    {
        "title": "Отношения в ORM",
        "description": "Modeling relationships with SQLAlchemy",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "How do you define relationships in SQLAlchemy?",
            "What is lazy loading vs eager loading?",
            "How do you handle many-to-many relationships?",
            "What is cascade?",
        ],
        "resources": [
            "https://docs.sqlalchemy.org/en/20/orm/relationships.html",
            "https://habr.com/ru/articles/556314/",
        ],
    },
    {
        "title": "Тестирование баз данных",
        "description": "Testing code that uses databases",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "How do you test database code?",
            "What are test fixtures?",
            "How do you handle test database setup?",
            "What is database seeding?",
        ],
        "resources": [
            "https://docs.pytest.org/en/stable/fixture.html",
            "https://habr.com/ru/articles/443626/",
        ],
    },
    {
        "title": "Основы Pytest",
        "description": "Testing with pytest framework",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "What are pytest fixtures?",
            "How do parametrize tests work?",
            "What is conftest.py?",
            "How do you mark and skip tests?",
        ],
        "resources": [
            "https://docs.pytest.org/",
            "https://habr.com/ru/articles/448792/",
        ],
    },
    {
        "title": "Моки и патчи",
        "description": "Using unittest.mock and pytest-mock",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "What is mocking?",
            "How does unittest.mock work?",
            "What's the difference between Mock and MagicMock?",
            "How do you patch objects?",
        ],
        "resources": [
            "https://docs.python.org/3/library/unittest.mock.html",
            "https://habr.com/ru/articles/450102/",
        ],
    },
    {
        "title": "Покрытие тестами",
        "description": "Measuring and improving test coverage",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "What is code coverage?",
            "How do you measure coverage with pytest-cov?",
            "What is a good coverage percentage?",
            "How do you identify untested code paths?",
        ],
        "resources": [
            "https://coverage.readthedocs.io/",
            "https://habr.com/ru/articles/151795/",
        ],
    },
    {
        "title": "Интеграционное тестирование",
        "description": "Testing multiple components together",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "What's the difference between unit and integration tests?",
            "How do you test API endpoints?",
            "What is the test pyramid?",
            "How do you use test containers?",
        ],
        "resources": [
            "https://testcontainers-python.readthedocs.io/",
            "https://habr.com/ru/articles/514120/",
        ],
    },
    {
        "title": "TDD и BDD",
        "description": "Test-driven and behavior-driven development",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "What is TDD?",
            "What is BDD and how does it differ from TDD?",
            "How do you write tests first?",
            "What are the benefits of TDD?",
        ],
        "resources": [
            "https://behave.readthedocs.io/",
            "https://habr.com/ru/articles/437142/",
        ],
    },
    {
        "title": "Тестирование производительности",
        "description": "Load testing and profiling",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "How do you profile Python code?",
            "What is load testing?",
            "How do you use pytest-benchmark?",
            "What tools exist for performance testing?",
        ],
        "resources": [
            "https://locust.io/",
            "https://habr.com/ru/articles/342132/",
        ],
    },
    {
        "title": "Основы Docker",
        "description": "Containerization with Docker",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "What is Docker and why use it?",
            "How do Dockerfiles work?",
            "What's the difference between image and container?",
            "What is multi-stage build?",
        ],
        "resources": [
            "https://docs.docker.com/get-started/",
            "https://habr.com/ru/articles/253877/",
        ],
    },
    {
        "title": "Docker Compose",
        "description": "Multi-container applications with Docker Compose",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "What is Docker Compose?",
            "How do services communicate?",
            "What are volumes and networks?",
            "How do you handle environment variables?",
        ],
        "resources": [
            "https://docs.docker.com/compose/",
            "https://habr.com/ru/articles/350640/",
        ],
    },
    {
        "title": "CI/CD пайплайны",
        "description": "Continuous integration and deployment",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "What is CI/CD?",
            "How do GitHub Actions work?",
            "What are pipeline stages?",
            "How do you automate testing and deployment?",
        ],
        "resources": [
            "https://docs.github.com/en/actions",
            "https://habr.com/ru/articles/504318/",
        ],
    },
    {
        "title": "Логирование и мониторинг",
        "description": "Application logging and monitoring best practices",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "How does Python logging work?",
            "What are logging levels?",
            "How do you structure logs?",
            "What is structured logging?",
        ],
        "resources": [
            "https://docs.python.org/3/library/logging.html",
            "https://habr.com/ru/articles/534126/",
        ],
    },
    {
        "title": "Управление окружением",
        "description": "Managing dependencies and environments",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "What's the difference between pip and poetry?",
            "How does virtual environment work?",
            "What is requirements.txt vs pyproject.toml?",
            "How do you handle dependency conflicts?",
        ],
        "resources": [
            "https://python-poetry.org/docs/",
            "https://habr.com/ru/articles/502120/",
        ],
    },
    {
        "title": "Управление конфигурацией",
        "description": "Managing application configuration",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "How do you handle configuration?",
            "What is the 12-factor app?",
            "How does pydantic-settings work?",
            "How do you manage secrets?",
        ],
        "resources": [
            "https://12factor.net/ru/",
            "https://pydantic-docs.helpmanual.io/usage/settings/",
        ],
    },
    {
        "title": "Порождающие паттерны",
        "description": "Singleton, Factory, Builder patterns",
        "category": "design_patterns",
        "difficulty": "middle",
        "questions": [
            "What is a Singleton pattern?",
            "How does Factory pattern work?",
            "When should you use Builder pattern?",
            "What are the downsides of Singleton?",
        ],
        "resources": [
            "https://refactoring.guru/ru/design-patterns/creational-patterns",
            "https://habr.com/ru/articles/463031/",
        ],
    },
    {
        "title": "Структурные паттерны",
        "description": "Adapter, Decorator, Facade patterns",
        "category": "design_patterns",
        "difficulty": "middle",
        "questions": [
            "What is Adapter pattern?",
            "How does Decorator pattern work in Python?",
            "What is Facade pattern?",
            "When should you use Proxy pattern?",
        ],
        "resources": [
            "https://refactoring.guru/ru/design-patterns/structural-patterns",
            "https://habr.com/ru/articles/463031/",
        ],
    },
    {
        "title": "Поведенческие паттерны",
        "description": "Strategy, Observer, Command patterns",
        "category": "design_patterns",
        "difficulty": "middle",
        "questions": [
            "What is Strategy pattern?",
            "How does Observer pattern work?",
            "What is Command pattern?",
            "When should you use State pattern?",
        ],
        "resources": [
            "https://refactoring.guru/ru/design-patterns/behavioral-patterns",
            "https://habr.com/ru/articles/463031/",
        ],
    },
    {
        "title": "Внедрение зависимостей",
        "description": "Implementing dependency injection in Python",
        "category": "design_patterns",
        "difficulty": "middle",
        "questions": [
            "What is dependency injection?",
            "How does it improve testability?",
            "What are DI containers?",
            "How does FastAPI's Depends work?",
        ],
        "resources": [
            "https://python-dependency-injector.ets-labs.org/",
            "https://habr.com/ru/articles/434400/",
        ],
    },
    {
        "title": "Паттерн Репозиторий",
        "description": "Data access layer abstraction",
        "category": "design_patterns",
        "difficulty": "middle",
        "questions": [
            "What is Repository pattern?",
            "How does it abstract data access?",
            "What is Unit of Work pattern?",
            "How do you implement Repository in Python?",
        ],
        "resources": [
            "https://cosmicpython.com/book/chapter_02_repository.html",
            "https://habr.com/ru/articles/556314/",
        ],
    },
    {
        "title": "Анализ сложности",
        "description": "Big O notation and algorithm complexity",
        "category": "algorithms",
        "difficulty": "middle",
        "questions": [
            "What is Big O notation?",
            "What's the difference between O(n) and O(log n)?",
            "How do you analyze space complexity?",
            "What is amortized complexity?",
        ],
        "resources": [
            "https://habr.com/ru/articles/104219/",
            "https://wiki.python.org/moin/TimeComplexity",
        ],
    },
    {
        "title": "Структуры данных",
        "description": "Common data structures in Python",
        "category": "algorithms",
        "difficulty": "middle",
        "questions": [
            "How do Python lists work internally?",
            "What's the difference between list and deque?",
            "When should you use sets vs lists?",
            "How do dictionaries achieve O(1) lookup?",
        ],
        "resources": [
            "https://docs.python.org/3/library/collections.html",
            "https://habr.com/ru/articles/430338/",
        ],
    },
    {
        "title": "Сортировка и поиск",
        "description": "Common algorithms for sorting and searching",
        "category": "algorithms",
        "difficulty": "middle",
        "questions": [
            "How does quicksort work?",
            "What is binary search?",
            "How does Python's sort work (Timsort)?",
            "When should you use heapq?",
        ],
        "resources": [
            "https://docs.python.org/3/library/heapq.html",
            "https://habr.com/ru/articles/188010/",
        ],
    },
    {
        "title": "Рекурсия и динамическое программирование",
        "description": "Solving problems with recursion and DP",
        "category": "algorithms",
        "difficulty": "middle",
        "questions": [
            "What is recursion?",
            "What is dynamic programming?",
            "What's the difference between memoization and tabulation?",
            "How do you use functools.lru_cache?",
        ],
        "resources": [
            "https://docs.python.org/3/library/functools.html",
            "https://habr.com/ru/articles/423939/",
        ],
    },
    {
        "title": "Принципы чистого кода",
        "description": "Writing readable and maintainable code",
        "category": "code_quality",
        "difficulty": "middle",
        "questions": [
            "What are SOLID principles?",
            "How do you write clean functions?",
            "What makes code readable?",
            "How do you handle code complexity?",
        ],
        "resources": [
            "https://habr.com/ru/articles/655403/",
            "https://habr.com/ru/articles/343270/",
        ],
    },
    {
        "title": "Лучшие практики Code Review",
        "description": "Effective code review techniques",
        "category": "code_quality",
        "difficulty": "middle",
        "questions": [
            "What makes a good code review?",
            "What should you look for in code reviews?",
            "How do you give constructive feedback?",
            "What are code review anti-patterns?",
        ],
        "resources": [
            "https://google.github.io/eng-practices/review/",
            "https://habr.com/ru/articles/451314/",
        ],
    },
    {
        "title": "Линтинг и форматирование",
        "description": "Automated code quality tools",
        "category": "code_quality",
        "difficulty": "middle",
        "questions": [
            "What is the difference between linter and formatter?",
            "How does ruff work?",
            "What is black and why use it?",
            "How do you configure pre-commit hooks?",
        ],
        "resources": [
            "https://docs.astral.sh/ruff/",
            "https://pre-commit.com/",
        ],
    },
    {
        "title": "Техники рефакторинга",
        "description": "Improving existing code structure",
        "category": "code_quality",
        "difficulty": "middle",
        "questions": [
            "What is refactoring?",
            "When should you refactor?",
            "What are common code smells?",
            "How do you refactor safely?",
        ],
        "resources": [
            "https://refactoring.guru/ru/refactoring",
            "https://habr.com/ru/articles/443568/",
        ],
    },
    {
        "title": "Проектирование API",
        "description": "Designing scalable and maintainable APIs",
        "category": "system_design",
        "difficulty": "middle",
        "questions": [
            "How do you design a good API?",
            "What is API versioning?",
            "How do you handle backward compatibility?",
            "What is rate limiting?",
        ],
        "resources": [
            "https://restfulapi.net/",
            "https://habr.com/ru/articles/483202/",
        ],
    },
    {
        "title": "Стратегии кэширования",
        "description": "Implementing caching for performance",
        "category": "system_design",
        "difficulty": "middle",
        "questions": [
            "What are caching strategies?",
            "What's the difference between Redis and Memcached?",
            "How does cache invalidation work?",
            "What is CDN caching?",
        ],
        "resources": [
            "https://habr.com/ru/articles/276413/",
            "https://redis.io/docs/",
        ],
    },
    {
        "title": "Очереди сообщений",
        "description": "Async communication with message queues",
        "category": "system_design",
        "difficulty": "middle",
        "questions": [
            "What is a message queue?",
            "How does RabbitMQ work?",
            "What is Celery?",
            "When should you use message queues?",
        ],
        "resources": [
            "https://habr.com/ru/articles/414459/",
            "https://www.rabbitmq.com/tutorials/tutorial-one-python.html",
        ],
    },
]


async def seed_topics() -> None:
    """Заполняет базу данных темами."""
    async with async_session_maker() as session:
        result = await session.execute(select(func.count()).select_from(Topic))
        count = result.scalar()

        if count > 0:
            print(f"Темы уже загружены ({count} тем существует)")
            return

        topics = []
        for topic_data in TOPICS:
            topic = Topic(
                title=topic_data["title"],
                description=topic_data["description"],
                category=topic_data["category"],
                difficulty=topic_data["difficulty"],
                questions=topic_data["questions"],
                resources=topic_data["resources"],
                is_active=True,
                times_used=0,
                avg_rating=0.0,
                created_at=datetime.now(UTC),
            )
            topics.append(topic)

        session.add_all(topics)
        await session.commit()

        print(f"Успешно загружено {len(topics)} тем")
        print("\nТемы по категориям:")
        categories: dict[str, int] = {}
        for topic in topics:
            categories[topic.category] = categories.get(topic.category, 0) + 1

        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")


if __name__ == "__main__":
    asyncio.run(seed_topics())
