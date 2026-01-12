"""Topic repository for data access."""

from sqlalchemy import and_, select
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

    async def get_by_category(self, category: str) -> list[Topic]:
        """Get all topics by category.

        Args:
            category: Topic category

        Returns:
            List of topics
        """
        result = await self.session.execute(select(Topic).where(Topic.category == category))
        return list(result.scalars().all())

    async def get_least_used_active_topics(
        self, difficulty: str, limit: int = 10
    ) -> list[Topic]:
        """Get least used active topics with difficulty.

        Args:
            difficulty: Difficulty level
            limit: Maximum number of topics to return

        Returns:
            List of topics ordered by usage
        """
        result = await self.session.execute(
            select(Topic)
            .where(
                and_(
                    Topic.is_active.is_(True),
                    Topic.difficulty == difficulty,
                )
            )
            .order_by(Topic.times_used)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_usage(self, topic_id: int) -> Topic | None:
        """Increment usage count for a topic.

        Args:
            topic_id: Topic ID

        Returns:
            Updated topic or None if not found
        """
        topic = await self.get_by_id(topic_id)
        if topic:
            topic.times_used += 1
            await self.session.flush()
            await self.session.refresh(topic)
        return topic  # type: ignore[no-any-return]
