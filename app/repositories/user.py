"""User repository for data access."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository.

        Args:
            session: Database session
        """
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User or None if not found
        """
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        level: str = "middle",
    ) -> User:
        """Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            level: User level (default: middle)

        Returns:
            User instance
        """
        user = await self.get_by_telegram_id(telegram_id)

        if user:
            # Update user info if changed
            if user.username != username:
                user.username = username
            if user.first_name != first_name:
                user.first_name = first_name
            if user.last_name != last_name:
                user.last_name = last_name
            await self.session.flush()
        else:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                level=level,
            )
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)

        return user

    async def mark_inactive(self, user_id: int) -> bool:
        """Mark user as inactive.

        Args:
            user_id: User ID

        Returns:
            True if user was found and marked inactive, False otherwise
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        await self.session.flush()
        return True

    async def get_active_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get active user by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            Active user or None
        """
        result = await self.session.execute(
            select(User).where(
                User.telegram_id == telegram_id,
                User.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]
