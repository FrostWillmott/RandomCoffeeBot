"""Helper functions for common business logic."""

from datetime import UTC, datetime
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.user import User
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository

T = TypeVar("T")


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """Get a user by their Telegram ID."""
    user_repo = UserRepository(session)
    return await user_repo.get_by_telegram_id(telegram_id)


async def get_next_open_session(session: AsyncSession) -> Session | None:
    """Get the next open session with the future registration deadline."""
    session_repo = SessionRepository(session)
    return await session_repo.get_next_open_session(datetime.now(UTC))


async def get_active_user(session: AsyncSession, telegram_id: int) -> User:
    """Get an active user or raise ValueError if not found/inactive."""
    user_repo = UserRepository(session)
    user = await user_repo.get_active_by_telegram_id(telegram_id)
    if not user:
        raise ValueError(f"User {telegram_id} not found or inactive")
    return user
