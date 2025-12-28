"""Seed database with Python Middle interview topics."""

import asyncio
from datetime import datetime

from sqlalchemy import func, select

from app.db.session import async_session_maker
from app.models.topic import Topic

TOPICS = [
    # Core Python (10 topics)
    {
        "title": "Decorators and closures",
        "description": "Understanding Python decorators, closures, and their practical applications",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What is a closure and how does it work?",
            "How do decorators work internally?",
            "What are class decorators vs function decorators?",
            "How would you create a decorator with arguments?",
        ],
        "resources": [
            "https://realpython.com/primer-on-python-decorators/",
            "https://docs.python.org/3/glossary.html#term-decorator",
        ],
    },
    {
        "title": "Context managers",
        "description": "Deep dive into context managers and the with statement",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What is a context manager?",
            "How do __enter__ and __exit__ work?",
            "When would you use contextlib.contextmanager?",
            "How do context managers help with resource management?",
        ],
        "resources": [
            "https://docs.python.org/3/library/contextlib.html",
            "https://realpython.com/python-with-statement/",
        ],
    },
    {
        "title": "Generators and iterators",
        "description": "Understanding generators, iterators, and lazy evaluation",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What's the difference between an iterator and an iterable?",
            "How do generators work? What is yield?",
            "What are generator expressions vs list comprehensions?",
            "When would you use itertools?",
        ],
        "resources": [
            "https://realpython.com/introduction-to-python-generators/",
            "https://docs.python.org/3/library/itertools.html",
        ],
    },
    {
        "title": "Metaclasses and descriptors",
        "description": "Advanced Python: metaclasses, descriptors, and the object model",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What is a metaclass?",
            "How do descriptors work (__get__, __set__, __delete__)?",
            "What's the difference between __new__ and __init__?",
            "How does attribute lookup work in Python?",
        ],
        "resources": [
            "https://realpython.com/python-metaclasses/",
            "https://docs.python.org/3/howto/descriptor.html",
        ],
    },
    {
        "title": "Memory management and GC",
        "description": "Understanding Python's memory model and garbage collection",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "How does Python manage memory?",
            "What is reference counting?",
            "How does the garbage collector work?",
            "What are circular references and how are they handled?",
        ],
        "resources": [
            "https://realpython.com/python-memory-management/",
            "https://docs.python.org/3/library/gc.html",
        ],
    },
    {
        "title": "GIL and concurrency",
        "description": "Global Interpreter Lock and its implications",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What is the GIL?",
            "How does the GIL affect multithreading?",
            "When should you use threading vs multiprocessing?",
            "How do asyncio and threading differ?",
        ],
        "resources": [
            "https://realpython.com/python-gil/",
            "https://docs.python.org/3/library/threading.html",
        ],
    },
    {
        "title": "Type hints and mypy",
        "description": "Static typing in Python with type hints",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "What are type hints and why use them?",
            "How does mypy work?",
            "What are generic types?",
            "How do you type decorators and higher-order functions?",
        ],
        "resources": [
            "https://realpython.com/python-type-checking/",
            "https://mypy.readthedocs.io/",
        ],
    },
    {
        "title": "Data classes and attrs",
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
            "https://realpython.com/python-data-classes/",
            "https://www.attrs.org/",
        ],
    },
    {
        "title": "Protocol and ABC",
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
        "title": "Python internals",
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
            "https://realpython.com/cpython-source-code-guide/",
            "https://docs.python.org/3/library/dis.html",
        ],
    },
    # Async Python (7 topics)
    {
        "title": "Asyncio fundamentals",
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
            "https://realpython.com/async-io-python/",
            "https://docs.python.org/3/library/asyncio.html",
        ],
    },
    {
        "title": "Async patterns",
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
            "https://realpython.com/python-async-features/",
        ],
    },
    {
        "title": "Async libraries",
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
        "title": "Async vs threading",
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
            "https://realpython.com/python-concurrency/",
            "https://docs.python.org/3/library/asyncio-eventloop.html",
        ],
    },
    {
        "title": "Async generators",
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
        "title": "Async debugging",
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
            "https://realpython.com/async-io-python/#debugging",
        ],
    },
    {
        "title": "Async testing",
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
            "https://realpython.com/python-async-testing/",
        ],
    },
    # Web Development (8 topics)
    {
        "title": "FastAPI fundamentals",
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
            "https://realpython.com/fastapi-python-web-apis/",
        ],
    },
    {
        "title": "REST API design",
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
            "https://realpython.com/api-integration-in-python/",
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
            "https://realpython.com/django-performance-optimization/",
        ],
    },
    {
        "title": "Authentication and authorization",
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
            "https://realpython.com/token-based-authentication-with-flask/",
            "https://fastapi.tiangolo.com/tutorial/security/",
        ],
    },
    {
        "title": "Middleware and CORS",
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
            "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS",
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
            "https://realpython.com/python-websockets/",
        ],
    },
    {
        "title": "API documentation",
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
        "title": "Request validation",
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
    # Databases (7 topics)
    {
        "title": "SQLAlchemy Core vs ORM",
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
            "https://realpython.com/python-sqlalchemy/",
        ],
    },
    {
        "title": "Database transactions",
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
            "https://realpython.com/python-sql-libraries/",
        ],
    },
    {
        "title": "Query optimization",
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
            "https://realpython.com/advanced-sql/",
        ],
    },
    {
        "title": "Database migrations",
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
            "https://realpython.com/alembic-migrations/",
        ],
    },
    {
        "title": "Connection pooling",
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
            "https://realpython.com/connection-pooling-with-sqlalchemy/",
        ],
    },
    {
        "title": "Relationships in ORM",
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
            "https://realpython.com/sqlalchemy-relationships/",
        ],
    },
    {
        "title": "Database testing",
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
            "https://realpython.com/testing-in-django-part-1-best-practices-and-examples/",
            "https://docs.pytest.org/en/stable/fixture.html",
        ],
    },
    # Testing (6 topics)
    {
        "title": "Pytest fundamentals",
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
            "https://realpython.com/pytest-python-testing/",
        ],
    },
    {
        "title": "Mocking and patching",
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
            "https://realpython.com/python-mock-library/",
            "https://docs.python.org/3/library/unittest.mock.html",
        ],
    },
    {
        "title": "Test coverage",
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
            "https://realpython.com/python-code-coverage/",
        ],
    },
    {
        "title": "Integration testing",
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
            "https://realpython.com/python-testing/",
            "https://testcontainers-python.readthedocs.io/",
        ],
    },
    {
        "title": "TDD and BDD",
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
            "https://realpython.com/python-testing/#test-driven-development",
            "https://behave.readthedocs.io/",
        ],
    },
    {
        "title": "Performance testing",
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
            "https://realpython.com/python-profiling/",
            "https://locust.io/",
        ],
    },
    # DevOps (6 topics)
    {
        "title": "Docker fundamentals",
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
            "https://realpython.com/docker-in-action-fitter-happier-more-productive/",
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
            "https://realpython.com/docker-compose-python/",
        ],
    },
    {
        "title": "CI/CD pipelines",
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
            "https://realpython.com/python-continuous-integration/",
        ],
    },
    {
        "title": "Logging and monitoring",
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
            "https://realpython.com/python-logging/",
        ],
    },
    {
        "title": "Environment management",
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
            "https://realpython.com/python-virtual-environments-a-primer/",
            "https://python-poetry.org/docs/",
        ],
    },
    {
        "title": "Configuration management",
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
            "https://12factor.net/",
            "https://pydantic-docs.helpmanual.io/usage/settings/",
        ],
    },
    # Design Patterns (5 topics)
    {
        "title": "Creational patterns",
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
            "https://refactoring.guru/design-patterns/creational-patterns",
            "https://realpython.com/factory-method-python/",
        ],
    },
    {
        "title": "Structural patterns",
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
            "https://refactoring.guru/design-patterns/structural-patterns",
            "https://realpython.com/primer-on-python-decorators/",
        ],
    },
    {
        "title": "Behavioral patterns",
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
            "https://refactoring.guru/design-patterns/behavioral-patterns",
            "https://realpython.com/python-design-patterns/",
        ],
    },
    {
        "title": "Dependency Injection",
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
            "https://fastapi.tiangolo.com/tutorial/dependencies/",
        ],
    },
    {
        "title": "Repository pattern",
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
            "https://realpython.com/python-design-patterns/",
        ],
    },
    # Data Structures & Algorithms (4 topics)
    {
        "title": "Complexity analysis",
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
            "https://realpython.com/python-time-complexity/",
            "https://wiki.python.org/moin/TimeComplexity",
        ],
    },
    {
        "title": "Data structures",
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
            "https://realpython.com/python-data-structures/",
            "https://docs.python.org/3/library/collections.html",
        ],
    },
    {
        "title": "Sorting and searching",
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
            "https://realpython.com/sorting-algorithms-python/",
            "https://docs.python.org/3/library/heapq.html",
        ],
    },
    {
        "title": "Recursion and dynamic programming",
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
            "https://realpython.com/python-recursion/",
            "https://docs.python.org/3/library/functools.html",
        ],
    },
    # Code Quality (4 topics)
    {
        "title": "Clean code principles",
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
            "https://realpython.com/python-pep8/",
            "https://realpython.com/python-refactoring/",
        ],
    },
    {
        "title": "Code review best practices",
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
            "https://realpython.com/python-code-quality/",
        ],
    },
    {
        "title": "Linting and formatting",
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
        "title": "Refactoring techniques",
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
            "https://refactoring.guru/refactoring",
            "https://realpython.com/python-refactoring/",
        ],
    },
    # System Design (3 topics)
    {
        "title": "API design",
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
            "https://realpython.com/api-integration-in-python/",
            "https://restfulapi.net/",
        ],
    },
    {
        "title": "Caching strategies",
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
            "https://realpython.com/python-redis/",
            "https://redis.io/docs/",
        ],
    },
    {
        "title": "Message queues",
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
            "https://realpython.com/asynchronous-tasks-with-django-and-celery/",
            "https://www.rabbitmq.com/tutorials/tutorial-one-python.html",
        ],
    },
]


async def seed_topics() -> None:
    """Seed database with topics."""
    async with async_session_maker() as session:
        # Check if topics already exist
        result = await session.execute(select(func.count()).select_from(Topic))
        count = result.scalar()

        if count > 0:
            print(f"Topics already seeded ({count} topics exist)")
            return

        # Create topics
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
                created_at=datetime.utcnow(),
            )
            topics.append(topic)

        session.add_all(topics)
        await session.commit()

        print(f"Successfully seeded {len(topics)} topics")
        print("\nTopics by category:")
        categories: dict[str, int] = {}
        for topic in topics:
            categories[topic.category] = categories.get(topic.category, 0) + 1

        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")


if __name__ == "__main__":
    asyncio.run(seed_topics())
