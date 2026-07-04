"""Session repository for data access."""

from datetime import datetime

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SessionStatus
from app.models.session import Session
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for Session entity."""

    def __init__(self, session: AsyncSession):
        """Initialize a session repository.

        Args:
            session: Database session
        """
        super().__init__(Session, session)

    async def get_by_date(self, date: datetime) -> Session | None:
        """Get session by date.

        Args:
            date: Session date

        Returns:
            Session or None if not found
        """
        result = await self.session.execute(select(Session).where(Session.date == date))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_next_open_session(self, current_time: datetime) -> Session | None:
        """Get next open session with future registration deadline.

        Args:
            current_time: Current datetime

        Returns:
            Next open session or None
        """
        result = await self.session.execute(
            select(Session)
            .where(
                Session.status == SessionStatus.OPEN,
                Session.registration_deadline > current_time,
            )
            .order_by(Session.date)
            .limit(1)
        )
        return result.scalars().first()  # type: ignore[no-any-return]

    async def get_sessions_by_status(self, status: SessionStatus) -> list[Session]:
        """Get all sessions with a specific status.

        Args:
            status: Session status

        Returns:
            List of sessions
        """
        result = await self.session.execute(select(Session).where(Session.status == status))
        return list(result.scalars().all())

    async def get_expired_open_sessions(self, current_time: datetime) -> list[Session]:
        """Get open sessions past their registration deadline.

        Args:
            current_time: Current datetime

        Returns:
            List of expired open sessions
        """
        result = await self.session.execute(
            select(Session).where(
                and_(
                    Session.status == SessionStatus.OPEN,
                    Session.registration_deadline < current_time,
                )
            )
        )
        return list(result.scalars().all())

    async def get_closed_sessions_ready_for_matching(
        self, current_time: datetime
    ) -> list[Session]:
        """Get closed sessions ready for matching.

        Args:
            current_time: Current datetime

        Returns:
            List of closed sessions
        """
        result = await self.session.execute(
            select(Session).where(
                and_(
                    Session.status == SessionStatus.CLOSED,
                    Session.registration_deadline < current_time,
                )
            )
        )
        return list(result.scalars().all())

    async def claim_for_matching(self, session_id: int) -> bool:
        """Atomically transition session from CLOSED to MATCHING.

        Uses UPDATE ... RETURNING so that exactly one caller in a
        concurrent race gets a row back: the winner receives the
        session id, the loser receives None.

        Args:
            session_id: Session ID to claim

        Returns:
            True if this caller successfully claimed the session
        """
        result = await self.session.execute(
            update(Session)
            .where(
                and_(
                    Session.id == session_id,
                    Session.status == SessionStatus.CLOSED,
                )
            )
            .values(status=SessionStatus.MATCHING)
            .returning(Session.id)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_announcement_message_id(self, message_id: int) -> Session | None:
        """Get session by announcement message ID.

        Args:
            message_id: Telegram message ID

        Returns:
            Session or None if not found
        """
        result = await self.session.execute(
            select(Session).where(Session.announcement_message_id == message_id)
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_matched_not_notified_sessions(self) -> list[Session]:
        """Get MATCHED sessions whose notifications have not been sent."""
        result = await self.session.execute(
            select(Session).where(
                and_(
                    Session.status == SessionStatus.MATCHED,
                    Session.notifications_sent_at.is_(None),
                )
            )
        )
        return list(result.scalars().all())

    async def get_open_unannounced_sessions(self) -> list[Session]:
        """Get OPEN sessions whose announcement has not been posted.

        Returns sessions with status OPEN and announcement_message_id IS NULL.
        """
        result = await self.session.execute(
            select(Session).where(
                and_(
                    Session.status == SessionStatus.OPEN,
                    Session.announcement_message_id.is_(None),
                )
            )
        )
        return list(result.scalars().all())

    async def get_open_session_by_announcement(self, message_id: int) -> Session | None:
        """Get open session by announcement message ID.

        Args:
            message_id: Telegram message ID

        Returns:
            Open session or None
        """
        result = await self.session.execute(
            select(Session).where(
                and_(
                    Session.announcement_message_id == message_id,
                    Session.status == SessionStatus.OPEN,
                )
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]
