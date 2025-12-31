"""Feedback repository for data access."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    """Repository for Feedback entity."""

    def __init__(self, session: AsyncSession):
        """Initialize feedback repository.

        Args:
            session: Database session
        """
        super().__init__(Feedback, session)

    async def get_by_match_id(self, match_id: int) -> list[Feedback]:
        """Get all feedback for a match.

        Args:
            match_id: Match ID

        Returns:
            List of feedback entries
        """
        result = await self.session.execute(
            select(Feedback).where(Feedback.match_id == match_id)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> list[Feedback]:
        """Get all feedback from a user.

        Args:
            user_id: User ID

        Returns:
            List of feedback entries
        """
        result = await self.session.execute(
            select(Feedback).where(Feedback.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_match_and_user(self, match_id: int, user_id: int) -> Feedback | None:
        """Get feedback by match and user.

        Args:
            match_id: Match ID
            user_id: User ID

        Returns:
            Feedback or None if not found
        """
        result = await self.session.execute(
            select(Feedback).where(
                and_(
                    Feedback.match_id == match_id,
                    Feedback.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def exists(self, match_id: int, user_id: int) -> bool:
        """Check if feedback exists for match and user.

        Args:
            match_id: Match ID
            user_id: User ID

        Returns:
            True if feedback exists, False otherwise
        """
        feedback = await self.get_by_match_and_user(match_id, user_id)
        return feedback is not None
