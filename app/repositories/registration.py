"""Registration repository for data access."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.registration import Registration
from app.repositories.base import BaseRepository


class RegistrationRepository(BaseRepository[Registration]):
    """Repository for Registration entity."""

    def __init__(self, session: AsyncSession):
        """Initialize registration repository.

        Args:
            session: Database session
        """
        super().__init__(Registration, session)

    async def get_by_session_and_user(
        self, session_id: int, user_id: int
    ) -> Registration | None:
        """Get registration by session and user.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            Registration or None if not found
        """
        result = await self.session.execute(
            select(Registration).where(
                and_(
                    Registration.session_id == session_id,
                    Registration.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_by_session_id(self, session_id: int) -> list[Registration]:
        """Get all registrations for a session.

        Args:
            session_id: Session ID

        Returns:
            List of registrations
        """
        result = await self.session.execute(
            select(Registration).where(Registration.session_id == session_id)
        )
        return list(result.scalars().all())

    async def get_by_session_id_with_users(self, session_id: int) -> list[Registration]:
        """Get all registrations for a session with user relations loaded.

        Args:
            session_id: Session ID

        Returns:
            List of registrations with user data
        """
        result = await self.session.execute(
            select(Registration)
            .options(selectinload(Registration.user))
            .where(Registration.session_id == session_id)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> list[Registration]:
        """Get all registrations for a user.

        Args:
            user_id: User ID

        Returns:
            List of registrations
        """
        result = await self.session.execute(
            select(Registration).where(Registration.user_id == user_id)
        )
        return list(result.scalars().all())

    async def exists(self, session_id: int, user_id: int) -> bool:
        """Check if registration exists.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            True if registration exists, False otherwise
        """
        registration = await self.get_by_session_and_user(session_id, user_id)
        return registration is not None
