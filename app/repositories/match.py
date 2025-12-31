"""Match repository for data access."""

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match
from app.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    """Repository for Match entity."""

    def __init__(self, session: AsyncSession):
        """Initialize match repository.

        Args:
            session: Database session
        """
        super().__init__(Match, session)

    async def get_by_session_id(self, session_id: int) -> list[Match]:
        """Get all matches for a session.

        Args:
            session_id: Session ID

        Returns:
            List of matches
        """
        result = await self.session.execute(
            select(Match).where(Match.session_id == session_id)
        )
        return list(result.scalars().all())

    async def get_by_session_id_with_relations(self, session_id: int) -> list[Match]:
        """Get all matches for a session with user and topic relations loaded.

        Args:
            session_id: Session ID

        Returns:
            List of matches with relations
        """
        result = await self.session.execute(
            select(Match)
            .options(
                selectinload(Match.user1),
                selectinload(Match.user2),
                selectinload(Match.topic),
            )
            .where(Match.session_id == session_id)
        )
        return list(result.scalars().all())

    async def get_previous_matches_for_users(
        self, user_ids: list[int]
    ) -> set[tuple[int, int]]:
        """Get all previous match pairs for given users.

        Args:
            user_ids: List of user IDs

        Returns:
            Set of sorted user ID pairs
        """
        if not user_ids:
            return set()

        result = await self.session.execute(
            select(Match.user1_id, Match.user2_id).where(
                or_(Match.user1_id.in_(user_ids), Match.user2_id.in_(user_ids))
            )
        )

        existing_pairs = set()
        for row in result.all():
            if row[0] is not None and row[1] is not None:
                existing_pairs.add(tuple(sorted((row[0], row[1]))))

        return existing_pairs

    async def get_matches_by_topic(self, topic_id: int) -> list[Match]:
        """Get all matches with specific topic.

        Args:
            topic_id: Topic ID

        Returns:
            List of matches
        """
        result = await self.session.execute(select(Match).where(Match.topic_id == topic_id))
        return list(result.scalars().all())

    async def get_matches_for_user(self, user_id: int) -> list[Match]:
        """Get all matches for a user.

        Args:
            user_id: User ID

        Returns:
            List of matches
        """
        result = await self.session.execute(
            select(Match).where(or_(Match.user1_id == user_id, Match.user2_id == user_id))
        )
        return list(result.scalars().all())

    async def get_topic_ids_used_by_users(self, user1_id: int, user2_id: int) -> set[int]:
        """Get all topic IDs used in matches involving these users.

        Args:
            user1_id: First user ID
            user2_id: Second user ID

        Returns:
            Set of topic IDs
        """
        result = await self.session.execute(
            select(Match.topic_id).where(
                and_(
                    Match.topic_id.isnot(None),
                    (Match.user1_id.in_([user1_id, user2_id]))
                    | (Match.user2_id.in_([user1_id, user2_id])),
                )
            )
        )
        return {row[0] for row in result.all() if row[0] is not None}
