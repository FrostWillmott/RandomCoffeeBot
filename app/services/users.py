"""User management service."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository

logger = logging.getLogger(__name__)


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    """Get existing user or create new one.

    Args:
        session: Database session
        telegram_id: Telegram user ID
        username: Telegram username
        first_name: User's first name
        last_name: User's last name

    Returns:
        User instance
    """
    user_repo = UserRepository(session)
    return await user_repo.get_or_create(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )
