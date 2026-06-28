# Discussion Topics Design

## 📋 Topic Structure

```python
class Topic:
    id: int
    title: str
    description: str
    category: str
    difficulty: str
    questions: list[str]
    resources: list[str]
    is_active: bool
    created_at: datetime
```

## 🎯 Topic Categories

### 1. Python Core
- Decorators and their applications
- Generators vs list comprehensions
- Context managers (with statement)
- Descriptors and property
- Metaclasses
- GIL and its impact
- Memory management and garbage collection

### 2. Async Programming
- asyncio basics
- async/await vs threading vs multiprocessing
- Event loop internals
- Async context managers
- Async generators
- Error handling in async code

### 3. Data Structures & Algorithms
- LRU cache implementation
- Search and sorting
- Trees and graphs
- Dynamic programming
- Time/Space complexity analysis

### 4. Frameworks (Django/FastAPI/Flask)
- ORM vs raw SQL
- Middleware and its usage
- Background tasks
- REST API design
- Authentication and authorization
- Query optimization (N+1 problem)

### 5. Databases
- Indexes and when to use them
- Transactions and ACID
- SQL JOIN types
- NoSQL vs SQL
- DB schema migrations
- Query optimization

### 6. Testing
- Unit vs Integration vs E2E
- Mocking and fixtures
- pytest best practices
- Test coverage
- TDD approach

### 7. System Design
- Application scaling
- Caching strategies
- Message queues (Celery, RabbitMQ)
- Microservices vs Monolith
- Load balancing

### 8. Best Practices
- Clean Code principles
- SOLID principles
- Design patterns (Factory, Singleton, Strategy, etc.)
- Code review practices
- Legacy code refactoring

### 9. DevOps for Developers
- Docker basics
- CI/CD pipelines
- Logging and monitoring
- Deployment strategies

### 10. Soft Skills
- Code review culture
- Teamwork
- Task planning
- Technical interviews - how to pass them

---

## 💾 Topic Sources

### Option 1: Pre-filled Database (Recommended for MVP)

**Pros:**
- Full quality control
- No dependency on external APIs
- Works offline
- Predictability

**Cons:**
- Requires manual work
- Needs periodic updates

**Implementation:**
```python
def upgrade():
    topics_data = [
        {
            "title": "Decorators in Python",
            "category": "python_core",
            "difficulty": "middle",
            "description": """
            Decorators are a powerful Python tool for modifying function behavior.
            It's important to understand how they work, when they are applied, and what patterns exist.
            """,
            "questions": [
                "What is a decorator and how does it work?",
                "What is the difference between @decorator and @decorator()?",
                "How to write a decorator with parameters?",
                "What does @functools.wraps do?",
                "Examples of using decorators in production code?"
            ],
            "resources": [
                "https://realpython.com/primer-on-python-decorators/",
                "https://peps.python.org/pep-0318/"
            ]
        },
    ]

    for topic in topics_data:
        op.execute(
            topics_table.insert().values(**topic)
        )
```

**Number of topics needed:** Minimum 50-70 for variety

---

### Option 2: AI Generation (For Scaling)

**Using OpenAI API for topic generation:**

```python
# app/services/ai_topic_generator.py
async def generate_topic(category: str, difficulty: str) -> dict:
    """Generates a topic via OpenAI API"""

    prompt = f"""
    Create a discussion topic for a Random Coffee meeting.

    Context: Preparing for a Middle Python Developer interview
    Category: {category}
    Difficulty: {difficulty}

    Return JSON:
    {{
        "title": "Brief topic name",
        "description": "2-3 sentences of description",
        "questions": ["5 specific questions for discussion"],
        "resources": ["2-3 links to materials"]
    }}
    """

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
```

**Pros:**
- Infinite variety
- Relevant topics
- Can be adapted for specific participants

**Cons:**
- Dependency on API
- API request costs
- Quality validation needed
- Possible hallucinations

---

### Option 3: Combined Approach (Optimal)

```python
class TopicService:
    def __init__(self):
        self.manual_topics = []
        self.ai_generated = []

    async def get_topic_for_match(self, match: Match) -> Topic:
        """Selects a topic for a pair"""

        if random.random() < 0.8:
            return await self._get_manual_topic(match)

        else:
            return await self._get_or_generate_ai_topic(match)

    async def _get_manual_topic(self, match: Match) -> Topic:
        """Selects from pre-filled topics"""
        used_topics = await self._get_used_topics(match.user1, match.user2)

        available = [t for t in self.manual_topics if t.id not in used_topics]

        return random.choice(available)
```

---

## 🎲 Topic Selection Algorithm

```python
async def select_topic_for_match(
    match: Match,
    user1: User,
    user2: User
) -> Topic:
    """
    Selects a suitable topic considering:
    1. Meeting history (avoid repeating topics)
    2. Participant level
    3. Preferences (optional)
    """

    discussed_topics = await get_discussed_topics(user1, user2)

    available_topics = await Topic.query.filter(
        Topic.id.not_in(discussed_topics),
        Topic.is_active == True,
        Topic.difficulty == "middle"
    ).all()

    if user_preferences := await get_user_preferences(user1, user2):
        available_topics = prioritize_by_preferences(
            available_topics,
            user_preferences
        )

    top_topics = random.sample(
        available_topics,
        min(10, len(available_topics))
    )

    return random.choice(top_topics)
```

---

## 📝 Topic Message Format

```
🎯 Your discussion topic:

**Decorators in Python**

Decorators are a powerful Python tool for modifying function behavior.
It's important to understand how they work, when they are applied, and what patterns exist.

💬 Questions for discussion:
1. What is a decorator and how does it work?
2. What is the difference between @decorator and @decorator()?
3. How to write a decorator with parameters?
4. What does @functools.wraps do?
5. Examples of using decorators in production code?

📚 Resources:
• https://realpython.com/primer-on-python-decorators/
• https://peps.python.org/pep-0318/

Enjoy your discussion! 😊
```

---

## 🔄 Topic Update System

### Automatic Replenishment
```python
# app/jobs/refresh_topics.py
async def weekly_topic_refresh():
    """Weekly replenishment of the topic database"""

    unused_count = await Topic.query.filter(
        Topic.times_used == 0
    ).count()

    if unused_count < 20:
        new_topics = await generate_topics_batch(
            count=10,
            categories=["python_core", "async", "databases"]
        )

        await Topic.bulk_create(new_topics)
```

### Manual Moderation
```python
# Admins can:
# 1. Add topics manually
# 2. Edit existing topics
# 3. Deactivate low-quality topics
# 4. View topic statistics (which ones are popular)
```

---

## 📊 Topic Metrics

```python
class Topic:

    times_used: int = 0
    avg_rating: float = 0.0
    last_used_at: datetime
```

This will allow:
- Removing unpopular topics
- Balancing usage frequency
- Improving topic quality based on feedback

---

## 🎯 Recommendation for MVP

**Start with Option 1 (pre-filled database):**

1. **Create 50-70 quality topics** manually
2. **Distribute by categories** (5-7 topics per category)
3. **Add via Alembic migration**
4. **In the future** - add AI generation for scaling

**Why this way:**
- ✅ Fast start without dependencies
- ✅ Guaranteed quality
- ✅ No API costs
- ✅ Can be iteratively improved
