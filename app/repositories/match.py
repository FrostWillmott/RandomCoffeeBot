"""Match repository for data access."""

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match
from app.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    """Repository for Match entity."""

    def __init__(self, session: AsyncSession):
        """Initialize a match repository.

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
                selectinload(Match.user3),
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
            Set of sorted user ID pairs (includes all pairs from triplets)
        """
        if not user_ids:
            return set()

        result = await self.session.execute(
            select(Match.user1_id, Match.user2_id, Match.user3_id).where(
                or_(
                    Match.user1_id.in_(user_ids),
                    Match.user2_id.in_(user_ids),
                    Match.user3_id.in_(user_ids),
                )
            )
        )

        existing_pairs = set()
        for row in result.all():
            user1_id, user2_id, user3_id = row
            if user1_id is not None and user2_id is not None:
                existing_pairs.add(tuple(sorted((user1_id, user2_id))))
            if user3_id is not None:
                if user1_id is not None:
                    existing_pairs.add(tuple(sorted((user1_id, user3_id))))
                if user2_id is not None:
                    existing_pairs.add(tuple(sorted((user2_id, user3_id))))

        return existing_pairs

    async def get_matches_by_topic(self, topic_id: int) -> list[Match]:
        """Get all matches with a specific topic.

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
            select(Match).where(
                or_(
                    Match.user1_id == user_id,
                    Match.user2_id == user_id,
                    Match.user3_id == user_id,
                )
            )
        )
        return list(result.scalars().all())

    async def get_topic_ids_used_by_users(self, *user_ids: int) -> set[int]:
        """Get all topic IDs used in matches involving these users.

        Args:
            *user_ids: Variable number of user IDs

        Returns:
            Set of topic IDs
        """
        if not user_ids:
            return set()

        result = await self.session.execute(
            select(Match.topic_id).where(
                and_(
                    Match.topic_id.isnot(None),
                    (Match.user1_id.in_(user_ids))
                    | (Match.user2_id.in_(user_ids))
                    | (Match.user3_id.in_(user_ids)),
                )
            )
        )
        return {row[0] for row in result.all() if row[0] is not None}
