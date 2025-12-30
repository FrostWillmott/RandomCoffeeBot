"""Helper functions for common business logic."""

from datetime import UTC, datetime
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SessionStatus
from app.models.session import Session
from app.models.user import User

T = TypeVar("T")


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """Get a user by their Telegram ID."""
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_next_open_session(session: AsyncSession) -> Session | None:
    """Get the next open session with future registration deadline."""
    result = await session.execute(
        select(Session)
        .where(
            Session.status == SessionStatus.OPEN,
            Session.registration_deadline > datetime.now(UTC),
        )
        .order_by(Session.date)
        .limit(1)
    )
    return result.scalars().first()


async def get_active_user(session: AsyncSession, telegram_id: int) -> User:
    """Get an active user or raise ValueError if not found/inactive."""
    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise ValueError(f"User {telegram_id} not found")
    if not user.is_active:
        raise ValueError(f"User {telegram_id} is inactive")
    return user
