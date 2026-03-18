"""Session management service."""

import logging
from datetime import UTC, datetime, timedelta

from app.constants import REGISTRATION_DURATION_DAYS
from app.models.enums import SessionStatus
from app.models.session import Session
from app.repositories.protocols import SessionRepositoryProtocol

logger = logging.getLogger(__name__)


async def create_weekly_session(
    session_repo: SessionRepositoryProtocol,
) -> Session:
    """Create a new Random Coffee session for the upcoming week.

    Args:
        session_repo: Session repository (caller creates from db session).

    Returns:
        Created or existing session.
    """
    now = datetime.now(UTC)
    days_ahead = 4 - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7

    session_date = (now + timedelta(days=days_ahead)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    registration_deadline = session_date - timedelta(days=REGISTRATION_DURATION_DAYS)

    old_open_sessions = await session_repo.get_sessions_by_status(SessionStatus.OPEN)
    for old_session in old_open_sessions:
        if old_session.date < session_date:
            old_session.status = SessionStatus.CLOSED
            await session_repo.update(old_session)
            logger.info(
                f"Closed old session {old_session.id} (date: {old_session.date}) "
                "before creating new session"
            )

    existing_session = await session_repo.get_by_date(session_date)

    if existing_session:
        logger.info(
            f"Session for {session_date} already exists with id {existing_session.id} "
            f"(status: {existing_session.status})"
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
