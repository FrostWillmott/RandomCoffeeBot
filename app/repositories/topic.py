"""Topic repository for data access."""

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic
from app.repositories.base import BaseRepository


class TopicRepository(BaseRepository[Topic]):
    """Repository for Topic entity."""

    def __init__(self, session: AsyncSession):
        """Initialize the topic repository.

        Args:
            session: Database session
        """
        super().__init__(Topic, session)

    async def get_active_by_difficulty(self, difficulty: str) -> list[Topic]:
        """Get all active topics by difficulty level.

        Args:
            difficulty: Difficulty level

        Returns:
            List of active topics
        """
        result = await self.session.execute(
            select(Topic).where(
                and_(
                    Topic.is_active.is_(True),
                    Topic.difficulty == difficulty,
                )
            )
        )
        return list(result.scalars().all())

    async def get_active(self) -> list[Topic]:
        """Get all active topics.

        Returns:
            List of active topics
        """
        result = await self.session.execute(select(Topic).where(Topic.is_active.is_(True)))
        return list(result.scalars().all())

    async def increment_usage(self, topic_id: int) -> Topic | None:
        """Increment usage count for a topic atomically.

        Uses a direct UPDATE to avoid the read-modify-write race.
        Returns the topic after increment (or None if not found).

        Args:
            topic_id: Topic ID

        Returns:
            Updated topic or None if not found
        """
        await self.session.execute(
            update(Topic)
            .where(Topic.id == topic_id)
            .values(times_used=Topic.times_used + 1)
        )
        await self.session.flush()
        return await self.get_by_id(topic_id)
