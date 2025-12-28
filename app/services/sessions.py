"""Session management service."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.enums import SessionStatus
from app.models.session import Session

logger = logging.getLogger(__name__)


async def create_weekly_session() -> Session | None:
    """Create a new Random Coffee session for the upcoming week."""
    async with async_session_maker() as db_session:
        try:
            now = datetime.now(UTC)
            days_ahead = 5 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7

            session_date = (now + timedelta(days=days_ahead)).replace(
                hour=10, minute=0, second=0, microsecond=0
            )

            registration_deadline = session_date - timedelta(days=1)

            result = await db_session.execute(
                select(Session).where(Session.date == session_date)
            )
            existing_session = result.scalar_one_or_none()

            if existing_session:
                logger.info(
                    f"Session for {session_date} already exists "
                    f"with id {existing_session.id}"
                )
                return existing_session

            session = Session(
                date=session_date,
                registration_deadline=registration_deadline,
                status=SessionStatus.OPEN,
                created_at=datetime.now(UTC),
            )
            db_session.add(session)
            await db_session.commit()
            await db_session.refresh(session)

            logger.info(
                f"Created new session {session.id} for {session_date} "
                f"(deadline: {registration_deadline})"
            )
            return session

        except Exception as e:
            logger.exception(
                "Error creating weekly session",
                exc_info=e,
            )
            await db_session.rollback()
            raise
