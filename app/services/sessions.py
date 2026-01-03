"""Session management service."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.enums import SessionStatus
from app.models.session import Session
from app.repositories.session import SessionRepository

logger = logging.getLogger(__name__)


async def create_weekly_session(
    db_session: AsyncSession | None = None,
) -> Session | None:
    """Create a new Random Coffee session for the upcoming week.

    Args:
        db_session: Optional database session. If not provided, creates a new one.

    Returns:
        Created or existing session
    """
    if db_session is None:
        async with async_session_maker() as session:
            try:
                result = await _create_weekly_session_logic(session)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
    else:
        return await _create_weekly_session_logic(db_session)


async def _create_weekly_session_logic(db_session: AsyncSession) -> Session:
    """Core logic for creating a weekly session."""
    session_repo = SessionRepository(db_session)

    now = datetime.now(UTC)
    days_ahead = 4 - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    session_date = (now + timedelta(days=days_ahead)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    registration_deadline = session_date - timedelta(days=1)

    existing_session = await session_repo.get_by_date(session_date)

    if existing_session:
        logger.info(
            f"Session for {session_date} already exists with id {existing_session.id}"
        )
        return existing_session

    session = Session(
        date=session_date,
        registration_deadline=registration_deadline,
        status=SessionStatus.OPEN,
        created_at=datetime.now(UTC),
    )
    created_session = await session_repo.create(session)

    logger.info(
        f"Created new session {created_session.id} for {session_date} "
        f"(deadline: {registration_deadline})"
    )
    return created_session
