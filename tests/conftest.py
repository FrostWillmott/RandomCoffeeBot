"""Test configuration and fixtures."""

import contextlib
import os

# Test database configuration (mock credentials for test environment only)
TEST_DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "randomcoffee_test")
TEST_DATABASE_HOST = os.getenv("TEST_DATABASE_HOST", "localhost")
TEST_DATABASE_PORT = os.getenv("TEST_DATABASE_PORT", "5434")
TEST_DATABASE_USER = os.getenv("TEST_DATABASE_USER", "postgres")  # nosec
TEST_DATABASE_PASSWORD = os.getenv("TEST_DATABASE_PASSWORD", "postgres")  # nosec

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+asyncpg://{TEST_DATABASE_USER}:{TEST_DATABASE_PASSWORD}@"
    f"{TEST_DATABASE_HOST}:{TEST_DATABASE_PORT}/{TEST_DATABASE_NAME}",
)

# Set environment variables BEFORE importing app modules
# Mock credentials for testing only (not real secrets)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"  # nosec
os.environ["TELEGRAM_BOT_TOKEN"] = "test:token"  # nosec
os.environ["CHANNEL_ID"] = "@test_channel"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

import itertools
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import Bot
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.models.enums import SessionStatus
from app.models.session import Session
from app.models.topic import Topic
from app.models.user import User

TEST_DATABASE_BASE_URL = os.getenv(
    "TEST_DATABASE_BASE_URL",
    f"postgresql+asyncpg://{TEST_DATABASE_USER}:{TEST_DATABASE_PASSWORD}@"
    f"{TEST_DATABASE_HOST}:{TEST_DATABASE_PORT}/postgres",
)


@pytest.fixture
def bot():
    """Create a mock bot instance."""
    bot = AsyncMock(spec=Bot)
    bot.id = 123456789
    return bot


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create an async database engine for tests.
    Creates a separate test database and ensures it's clean.
    Each test runs in an isolated transaction that gets rolled back.
    """
    admin_engine = create_async_engine(
        TEST_DATABASE_BASE_URL,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
    )

    async with admin_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": TEST_DATABASE_NAME},
        )
        exists = result.scalar()

        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{TEST_DATABASE_NAME}"'))
    await admin_engine.dispose()
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for a test.

    Each test runs in an isolated transaction which is automatically
    rolled back after the test completes. This ensures test isolation
    without needing to clean up data manually.
    """
    async with db_engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        try:
            yield session
        finally:
            with contextlib.suppress(Exception):
                if transaction.is_active:
                    await transaction.rollback()
            with contextlib.suppress(Exception):
                await session.close()


_user_counter = itertools.count(start=10000)
_session_counter = itertools.count(start=1)
_topic_counter = itertools.count(start=1)


@pytest_asyncio.fixture
async def user_factory(db_session):
    """Factory for creating test users.

    Usage:
        user = await user_factory(username="test_user")
        user = await user_factory()
    """

    async def _create_user(
        username: str | None = None,
        telegram_id: int | None = None,
        first_name: str | None = None,
        is_active: bool = True,
    ) -> User:
        tid = telegram_id or next(_user_counter)
        user = User(
            telegram_id=tid,
            username=username or f"user_{tid}",
            first_name=first_name or f"User {tid}",
            is_active=is_active,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def session_factory(db_session):
    """Factory for creating test sessions.

    Usage:
        session = await session_factory()
        session = await session_factory(days_ahead=7,
         status=SessionStatus.CLOSED)
    """

    async def _create_session(
        days_ahead: int = 5,
        status: SessionStatus = SessionStatus.OPEN,
        registration_deadline_days_before: int = 1,
    ) -> Session:
        now = datetime.now(UTC)
        session_date = now + timedelta(days=days_ahead)
        reg_deadline = session_date - timedelta(days=registration_deadline_days_before)

        sess = Session(
            date=session_date,
            registration_deadline=reg_deadline,
            status=status,
            created_at=now,
        )
        db_session.add(sess)
        await db_session.commit()
        await db_session.refresh(sess)
        return sess

    return _create_session


@pytest_asyncio.fixture
async def topic_factory(db_session):
    """Factory for creating test topics.

    Usage:
        topic = await topic_factory(title="Test Topic")
        topic = await topic_factory()
    """

    async def _create_topic(
        title: str | None = None,
        description: str = "Test description",
        category: str = "test",
        difficulty: str = "middle",
        is_active: bool = True,
    ) -> Topic:
        topic_id = next(_topic_counter)
        topic = Topic(
            title=title or f"Topic {topic_id}",
            description=description,
            category=category,
            difficulty=difficulty,
            questions=["Q1", "Q2"],
            resources=[],
            is_active=is_active,
        )
        db_session.add(topic)
        await db_session.commit()
        await db_session.refresh(topic)
        return topic

    return _create_topic
