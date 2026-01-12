"""Session repository for data access."""

from datetime import datetime

from sqlalchemy import and_, select
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
