"""Заполнение базы данных темами для интервью Python Middle."""

import asyncio
from datetime import UTC, datetime

from sqlalchemy import func, select

from app.db.session import async_session_maker
from app.models.topic import Topic

TOPICS = [
    {
        "title": "Объектно-ориентированное программирование в Python",
        "description": "Глубокое понимание ООП: наследование, полиморфизм, инкапсуляция,"
        " принципы SOLID, метаклассы, дескрипторы и магические методы",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Объясните difference между классическим наследованием и композицией."
            " Когда использовать каждый подход?",
            "Как работает Method Resolution Order (MRO) в множественном наследовании?"
            " Что такое алгоритм C3 linearization?",
            "В чем разница между __new__ и __init__? Приведите примеры,"
            " когда нужно переопределять __new__",
            "Объясните принципы SOLID на конкретных примерах."
            " Как они помогают в проектировании?",
            "Что такое дескрипторы и как они используются в Python? Как работают property,"
            " staticmethod, classmethod?",
            "Объясните концепцию метаклассов. Когда их стоит использовать,"
            " а когда это overkill?",
            "Как работает поиск атрибутов в Python? Что происходит при вызове obj.attr?",
            "В чем разница между абстрактными базовыми классами"
            " и протоколами для обеспечения полиморфизма?",
        ],
        "resources": [
            "https://docs.python.org/3/reference/datamodel.html",
            "https://habr.com/ru/articles/145835/",
            "https://docs.python.org/3/howto/descriptor.html",
            "https://peps.python.org/pep-0544/",
        ],
    },
    {
        "title": "Функциональное программирование и продвинутые возможности Python",
        "description": "Функции первого класса, замыкания, декораторы, генераторы,"
        " итераторы, функциональные паттерны",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Объясните концепцию замыканий."
            " Как они работают в Python"
            " и какие проблемы могут возникнуть?",
            "В чем разница между генератором и итератором? Когда использовать каждый?",
            "Как работают декораторы внутри? Что такое wraps и зачем он нужен?",
            "Объясните lazy evaluation в Python."
            " Где она используется и какие дает преимущества?",
            "Что такое comprehensions? Какие виды бывают и как они работают под капотом?",
            "В чем разница между map/filter/reduce и list comprehensions?"
            " Что быстрее и почему?",
            "Как работает модуль functools? Объясните partial, singledispatch, lru_cache",
            "Что такое context manager и как его создать несколькими способами?",
        ],
        "resources": [
            "https://docs.python.org/3/library/functools.html",
            "https://docs.python.org/3/library/contextlib.html",
            "https://habr.com/ru/articles/488112/",
            "https://docs.python.org/3/library/itertools.html",
        ],
    },
    {
        "title": "Управление памятью, производительность и внутреннее устройство Python",
        "description": "Модель памяти Python, garbage collection, GIL,"
        " оптимизация производительности, профилирование",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "Как Python управляет памятью? Объясните reference counting"
            " и циклические ссылки",
            "Что такое GIL и почему он существует? Как влияет на многопоточность?",
            "Объясните работу garbage collector в Python. Что такое поколения объектов?",
            "В чем разница между CPython, PyPy, Jython? Какие есть альтернативы GIL?",
            "Как работают словари в Python? Почему lookup O(1) и что может это нарушить?",
            "Что такое interning в Python? Для каких объектов он применяется?",
            "Объясните difference между deep copy и shallow copy. Когда важно различие?",
            "Как профилировать Python код?"
            " Какие инструменты использовать для поиска bottleneck?",
            "Что такое slots и когда их использовать? Какие ограничения они накладывают?",
        ],
        "resources": [
            "https://habr.com/ru/articles/417559/",
            "https://docs.python.org/3/library/gc.html",
            "https://habr.com/ru/articles/84629/",
            "https://docs.python.org/3/library/dis.html",
        ],
    },
    {
        "title": "Типизация и статический анализ кода",
        "description": "Type hints, mypy, Generic типы, Protocol, TypeVar,"
        " статическая типизация в больших проектах",
        "category": "core_python",
        "difficulty": "middle",
        "questions": [
            "В чем преимущества статической типизации?"
            " Как type hints влияют на производительность?",
            "Объясните концепцию structural typing vs nominal typing в Python",
            "Как работают Generic типы? В чем разница между TypeVar, Generic, Protocol?",
            "Что такое variance в типизации? Объясните covariance,"
            " contravariance, invariance",
            "Как типизировать функции высшего порядка и декораторы?",
            "В чем разница между Optional[T] и Union[T, None]? Что лучше использовать?",
            "Как настроить mypy для legacy проекта?"
            " Какие стратегии постепенного внедрения?",
            "Объясните концепцию Literal types и когда они полезны",
            "Что такое TypedDict и как он помогает с типизацией словарей?",
        ],
        "resources": [
            "https://mypy.readthedocs.io/",
            "https://peps.python.org/pep-0484/",
            "https://peps.python.org/pep-0544/",
            "https://habr.com/ru/articles/346542/",
        ],
    },
    {
        "title": "Асинхронное программирование: концепции и архитектура",
        "description": "Event loop, корутины, concurrency models, async/await,"
        " выбор между threading/asyncio/multiprocessing",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "Объясните разницу между concurrency и parallelism. Что предоставляет asyncio?",
            "Как работает event loop? Что происходит под капотом при await?",
            "В чем разница между корутиной, задачей и future в asyncio?",
            "Когда выбрать asyncio, threading или multiprocessing?"
            " Приведите критерии выбора",
            "Что такое back pressure и как с ним бороться в асинхронных системах?",
            "Объясните проблему function coloring в async/await. Есть ли решения?",
            "Как работает cooperative multitasking? В чем его преимущества и недостатки?",
            "Что происходит при блокирующем вызове в async функции? Как этого избежать?",
            "Объясните концепцию async context managers и async iterators",
        ],
        "resources": [
            "https://docs.python.org/3/library/asyncio.html",
            "https://habr.com/ru/articles/337420/",
            "https://peps.python.org/pep-0492/",
            "https://peps.python.org/pep-0525/",
        ],
    },
    {
        "title": "Параллелизм и многопоточность в Python",
        "description": "Threading, multiprocessing, concurrent.futures, синхронизация,"
        " race conditions, deadlocks",
        "category": "async_programming",
        "difficulty": "middle",
        "questions": [
            "Объясните разницу между thread-safe и atomic операциями в Python",
            "Какие проблемы решает модуль concurrent.futures?"
            " ThreadPoolExecutor vs ProcessPoolExecutor",
            "Что такое race condition? Как их предотвратить в Python?",
            "Объясните различные типы locks: Lock, RLock, Semaphore, Condition",
            "Что такое deadlock и как его избежать? Какие есть стратегии обнаружения?",
            "Как работает межпроцессное взаимодействие в multiprocessing?",
            "В чем разница между daemon и non-daemon потоками/процессами?",
            "Объясните концепцию thread-local storage. Когда она полезна?",
            "Как GIL влияет на производительность CPU-bound vs I/O-bound задач?",
        ],
        "resources": [
            "https://docs.python.org/3/library/threading.html",
            "https://docs.python.org/3/library/multiprocessing.html",
            "https://docs.python.org/3/library/concurrent.futures.html",
            "https://habr.com/ru/articles/84629/",
        ],
    },
    {
        "title": "Архитектура веб-приложений и HTTP протокол",
        "description": "HTTP/HTTPS, RESTful API design, статусы ответов, заголовки,"
        " кеширование, безопасность",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "Объясните жизненный цикл HTTP запроса от браузера до сервера и обратно",
            "В чем разница между HTTP/1.1, HTTP/2 и HTTP/3?"
            " Какие проблемы решает каждая версия?",
            "Как работает HTTPS? Что происходит во время TLS handshake?",
            "Объясните принципы REST. Что делает API RESTful?",
            "Какие HTTP статус коды должен знать backend разработчик?"
            " Когда использовать 4xx vs 5xx?",
            "Как работают HTTP заголовки? Объясните Cache-Control, ETag, Authorization",
            "Что такое CORS и почему он нужен? Как работают preflight запросы?",
            "Объясните различные методы аутентификации: Basic, Bearer, OAuth 2.0, JWT",
            "Как обеспечить idempotency в API? Почему это важно?",
        ],
        "resources": [
            "https://developer.mozilla.org/ru/docs/Web/HTTP",
            "https://restfulapi.net/",
            "https://developer.mozilla.org/ru/docs/Web/HTTP/CORS",
            "https://habr.com/ru/articles/483202/",
        ],
    },
    {
        "title": "Безопасность веб-приложений",
        "description": "OWASP Top 10, аутентификация, авторизация, SQL injection, XSS,"
        " CSRF, шифрование",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "Объясните основные угрозы из OWASP Top 10. Как защититься от каждой?",
            "В чем разница между аутентификацией и авторизацией? Как реализовать RBAC?",
            "Как работает SQL injection?"
            " Какие есть методы защиты кроме prepared statements?",
            "Что такое XSS атаки? В чем разница между reflected, stored и DOM-based XSS?",
            "Объясните CSRF атаки. Как CSRF токены защищают от них?",
            "Как безопасно хранить пароли? Что такое salt и почему bcrypt лучше MD5?",
            "Что такое JWT токены? В чем их преимущества и недостатки для аутентификации?",
            "Объясните принципы least privilege и defense in depth",
            "Как обеспечить безопасность API? Rate limiting, input validation, logging",
        ],
        "resources": [
            "https://owasp.org/www-project-top-ten/",
            "https://cheatsheetseries.owasp.org/",
            "https://habr.com/ru/articles/340146/",
            "https://jwt.io/introduction/",
        ],
    },
    {
        "title": "Микросервисы и распределенные системы",
        "description": "Архитектурные паттерны, service discovery, load balancing,"
        " circuit breaker, distributed transactions",
        "category": "web_development",
        "difficulty": "middle",
        "questions": [
            "В чем преимущества и недостатки микросервисной архитектуры vs монолита?",
            "Как организовать communication между микросервисами? Sync vs async подходы",
            "Что такое service discovery и зачем он нужен в микросервисах?",
            "Объясните паттерн Circuit Breaker. Как он помогает обеспечить resilience?",
            "Что такое distributed transactions?"
            " Объясните паттерны Saga и Two-Phase Commit",
            "Как обеспечить data consistency в distributed системах? CAP theorem",
            "Что такое API Gateway и какие проблемы он решает?",
            "Объясните стратегии деплоя микросервисов: blue-green, canary, rolling updates",
            "Как организовать monitoring и logging в микросервисной архитектуре?",
        ],
        "resources": [
            "https://microservices.io/patterns/",
            "https://martinfowler.com/articles/microservices.html",
            "https://habr.com/ru/articles/249183/",
            "https://12factor.net/",
        ],
    },
    {
        "title": "Теория баз данных и SQL",
        "description": "ACID, нормализация, индексы, транзакции, блокировки,"
        " репликация, шардинг",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "Объясните ACID свойства транзакций. Приведите примеры нарушения каждого",
            "Что такое нормализация БД? Объясните 1NF, 2NF, 3NF, BCNF."
            " Когда денормализовать?",
            "Как работают индексы? B-tree vs Hash vs Bitmap индексы."
            " Когда использовать каждый?",
            "В чем разница между clustered и non-clustered индексами?",
            "Объясните уровни изоляции транзакций. Какие проблемы решает каждый уровень?",
            "Что такое deadlock в базе данных? Как СУБД их обнаруживает и разрешает?",
            "Объясните различные типы joins в SQL. Когда использовать каждый?",
            "Как работает оптимизатор запросов? Что такое query execution plan?",
            "В чем разница между OLTP и OLAP системами?",
        ],
        "resources": [
            "https://www.postgresql.org/docs/current/",
            "https://habr.com/ru/articles/463669/",
            "https://habr.com/ru/articles/276633/",
            "https://use-the-index-luke.com/",
        ],
    },
    {
        "title": "NoSQL базы данных и выбор хранилища",
        "description": "Document, Key-Value, Column-family, Graph БД. MongoDB,"
        " Redis, Elasticsearch. CAP theorem",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "Объясните типы NoSQL баз данных. Когда использовать каждый тип?",
            "В чем разница между SQL и NoSQL? Критерии выбора для проекта",
            "Что такое CAP theorem? Объясните на примерах разных БД",
            "Как работает MongoDB? Что такое document store и когда его выбрать?",
            "Объясните концепцию eventual consistency. В каких системах она приемлема?",
            "Как работает Redis? В чем разница между различными структурами данных?",
            "Что такое sharding и partitioning? Horizontal vs vertical partitioning",
            "Объясните стратегии репликации: master-slave, master-master",
            "Как обеспечить backup и recovery в NoSQL системах?",
        ],
        "resources": [
            "https://redis.io/docs/",
            "https://docs.mongodb.com/",
            "https://habr.com/ru/articles/152477/",
            "https://martinfowler.com/articles/nosql-intro.html",
        ],
    },
    {
        "title": "ORM и паттерны работы с данными",
        "description": "SQLAlchemy архитектура, Active Record vs Data Mapper,"
        " Unit of Work, Repository pattern",
        "category": "databases",
        "difficulty": "middle",
        "questions": [
            "В чем разница между Active Record и Data Mapper паттернами?",
            "Объясните архитектуру SQLAlchemy: Core vs ORM. Когда использовать каждый?",
            "Что такое Unit of Work паттерн? Как SQLAlchemy его реализует?",
            "Объясните lazy loading vs eager loading. Проблема N+1 запросов",
            "Как работает identity map в ORM? Зачем он нужен?",
            "Что такое Repository паттерн? Как он помогает тестируемости?",
            "Объясните различные стратегии маппинга наследования в ORM",
            "Как обрабатывать optimistic vs pessimistic locking в ORM?",
            "В чем преимущества и недостатки использования ORM vs raw SQL?",
        ],
        "resources": [
            "https://docs.sqlalchemy.org/en/20/",
            "https://martinfowler.com/eaaCatalog/",
            "https://cosmicpython.com/book/chapter_02_repository.html",
            "https://habr.com/ru/articles/556314/",
        ],
    },
    {
        "title": "Тестирование: стратегии и лучшие практики",
        "description": "Test pyramid, виды тестов, TDD/BDD, мокирование,"
        " coverage, тестирование в CI/CD",
        "category": "testing",
        "difficulty": "middle",
        "questions": [
            "Объясните test pyramid. В чем разница между unit, integration, e2e тестами?",
            "Что такое TDD и BDD? В чем философская разница между подходами?",
            "Когда использовать мокирование? В чем разница между mock, stub, spy, fake?",
            "Как измерить качество тестов? Что такое mutation testing?",
            "Объясните принципы FIRST для unit тестов. Что такое test smells?",
            "Как тестировать legacy код без существующих тестов? Characterization tests",
            "Что такое contract testing? Как обеспечить совместимость между сервисами?",
            "Объясните различные стратегии test data management",
            "Как организовать тестирование в microservices архитектуре?",
        ],
        "resources": [
            "https://martinfowler.com/articles/practical-test-pyramid.html",
            "https://docs.pytest.org/en/stable/",
            "https://habr.com/ru/articles/448792/",
            "https://testcontainers.org/",
        ],
    },
    {
        "title": "DevOps и инфраструктура для Python приложений",
        "description": "Контейнеризация, CI/CD, мониторинг,"
        " deployment strategies, infrastructure as code",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "Объясните принципы 12-factor app. Как они влияют на архитектуру приложения?",
            "В чем разница между контейнерами и виртуальными машинами?",
            "Что такое infrastructure as code? Terraform vs Ansible vs CloudFormation",
            "Объясните различные deployment strategies: rolling, blue-green, canary",
            "Как организовать CI/CD pipeline? Какие стадии должны быть обязательно?",
            "Что такое observability? Metrics, logs,"
            " traces - как они дополняют друг друга?",
            "Объясните концепцию immutable infrastructure. В чем преимущества?",
            "Как обеспечить security в DevOps pipeline? DevSecOps practices",
            "Что такое chaos engineering и зачем он нужен?",
        ],
        "resources": [
            "https://12factor.net/",
            "https://docs.docker.com/",
            "https://kubernetes.io/docs/concepts/",
            "https://martinfowler.com/articles/continuousIntegration.html",
        ],
    },
    {
        "title": "Мониторинг и observability",
        "description": "Metrics, logging, tracing, APM, алерты,"
        " SLA/SLO, performance monitoring",
        "category": "devops",
        "difficulty": "middle",
        "questions": [
            "В чем разница между monitoring и observability?",
            "Объясните три pillars of observability: metrics, logs, traces",
            "Что такое SLA, SLO, SLI? Как они связаны с error budget?",
            "Как проектировать effective алерты? Что такое alert fatigue?",
            "Объясните различные типы метрик: counters, gauges, histograms, summaries",
            "Что такое distributed tracing? Как он помогает в debugging микросервисов?",
            "Как организовать centralized logging? ELK stack vs alternatives",
            "Объясните концепцию RED и USE методологий для мониторинга",
            "Как мониторить производительность Python приложений? APM tools",
        ],
        "resources": [
            "https://sre.google/sre-book/",
            "https://opentelemetry.io/docs/",
            "https://prometheus.io/docs/",
            "https://habr.com/ru/articles/534126/",
        ],
    },
    {
        "title": "Архитектурные паттерны и принципы проектирования",
        "description": "SOLID, DDD, Clean Architecture, CQRS, Event Sourcing, паттерны GoF",
        "category": "design_patterns",
        "difficulty": "middle",
        "questions": [
            "Объясните принципы SOLID на конкретных примерах. Как они влияют на код?",
            "Что такое Domain Driven Design? Объясните bounded context,"
            " aggregates, entities",
            "Объясните Clean Architecture. Как организовать dependency direction?",
            "Что такое CQRS? Когда этот паттерн оправдан, а когда overengineering?",
            "Объясните Event Sourcing. В чем преимущества и сложности этого подхода?",
            "Как выбрать подходящий архитектурный паттерн для проекта?",
            "Объясните разницу между Layered и Hexagonal architecture",
            "Что такое Dependency Injection? Как он помогает тестируемости?",
            "Объясните паттерны из GoF, наиболее важные для backend разработки",
        ],
        "resources": [
            "https://refactoring.guru/design-patterns",
            "https://martinfowler.com/architecture/",
            "https://cosmicpython.com/book/",
            "https://habr.com/ru/articles/463031/",
        ],
    },
    {
        "title": "Алгоритмы и структуры данных: теория и применение",
        "description": "Сложность алгоритмов, основные структуры данных,"
        " алгоритмы сортировки и поиска",
        "category": "algorithms",
        "difficulty": "middle",
        "questions": [
            "Объясните Big O notation."
            " Как анализировать время и пространственную сложность?",
            "В чем разница между worst-case, average-case, best-case complexity?",
            "Объясните работу различных структур данных: array,"
            " linked list, hash table, tree",
            "Как работают hash tables? Что такое collision resolution strategies?",
            "Объясните различные алгоритмы сортировки: их сложность и применимость",
            "Что такое balanced trees? B-trees, Red-Black trees, AVL trees",
            "Объясните graph algorithms: BFS, DFS, Dijkstra, топологическая сортировка",
            "Что такое dynamic programming? Memoization vs tabulation",
            "Как выбрать подходящую структуру данных для конкретной задачи?",
        ],
        "resources": [
            "https://wiki.python.org/moin/TimeComplexity",
            "https://habr.com/ru/articles/104219/",
            "https://visualgo.net/",
            "https://docs.python.org/3/library/collections.html",
        ],
    },
    {
        "title": "Производительность и оптимизация",
        "description": "Профилирование, bottleneck анализ,"
        " кеширование, database optimization, memory optimization",
        "category": "performance",
        "difficulty": "middle",
        "questions": [
            "Как подойти к оптимизации производительности? Measure first principle",
            "Объясните различные виды bottlenecks: CPU, I/O, memory, network",
            "Какие инструменты профилирования Python вы знаете?"
            " cProfile, py-spy, line_profiler",
            "Объясните стратегии кеширования: где, что и как долго кешировать?",
            "Что такое cache invalidation? Какие стратегии существуют?",
            "Как оптимизировать работу с базой данных? Query optimization, indexing",
            "Объясните концепцию memory pooling и object pooling",
            "Что такое premature optimization и как её избежать?",
            "Как измерить и улучшить latency vs throughput системы?",
        ],
        "resources": [
            "https://docs.python.org/3/library/profile.html",
            "https://habr.com/ru/articles/276413/",
            "https://use-the-index-luke.com/",
            "https://habr.com/ru/articles/342132/",
        ],
    },
    {
        "title": "Системное проектирование: высоконагруженные системы",
        "description": "Scalability, availability, consistency,"
        " partitioning, load balancing, caching strategies",
        "category": "system_design",
        "difficulty": "middle",
        "questions": [
            "Как спроектировать систему для миллионов пользователей?"
            " Horizontal vs vertical scaling",
            "Объясните CAP theorem на практических примерах разных систем",
            "Что такое consistent hashing? Как он помогает в distributed systems?",
            "Объясните различные стратегии load balancing: round-robin,"
            " least connections, etc",
            "Как обеспечить high availability? Fault tolerance patterns",
            "Что такое data partitioning/sharding? Какие стратегии существуют?",
            "Объясните eventual consistency vs strong consistency. Trade-offs",
            "Как проектировать для disaster recovery? RTO vs RPO",
            "Что такое bulkhead pattern и circuit breaker в системной архитектуре?",
        ],
        "resources": [
            "https://github.com/donnemartin/system-design-primer",
            "https://martinfowler.com/articles/patterns-of-distributed-systems/",
            "https://habr.com/ru/articles/414459/",
            "https://sre.google/sre-book/",
        ],
    },
    {
        "title": "Качество кода и инженерные практики",
        "description": "Code review, рефакторинг, техническийдолг,"
        " code style, статический анализ",
        "category": "code_quality",
        "difficulty": "middle",
        "questions": [
            "Что делает код качественным? Принципы clean code",
            "Как проводить effective code review? Что искать в чужом коде?",
            "Что такое технический долг? Как им управлять в долгосрочной перспективе?",
            "Объясните code smells. Какие наиболее критичные для Python?",
            "Как организовать рефакторинг legacy кода без регрессий?",
            "Зачем нужны coding standards? Как их внедрить в команде?",
            "Что такое static analysis? Linting vs type checking vs security scanning",
            "Как измерить maintainability кода? Цикломатическая сложность и другие метрики",
            "Объясните принципы DRY, KISS, YAGNI. Когда они конфликтуют?",
        ],
        "resources": [
            "https://refactoring.guru/refactoring",
            "https://google.github.io/eng-practices/review/",
            "https://docs.astral.sh/ruff/",
            "https://habr.com/ru/articles/655403/",
        ],
    },
]


async def seed_topics() -> None:
    """Заполняет базу данных темами."""
    async with async_session_maker() as session:
        result = await session.execute(select(func.count()).select_from(Topic))
        count = result.scalar()

        if count is not None and count > 0:
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
