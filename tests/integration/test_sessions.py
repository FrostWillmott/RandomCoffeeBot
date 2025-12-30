"""Integration tests for sessions service."""

from datetime import UTC, datetime

import pytest

from app.models.enums import SessionStatus
from app.models.session import Session
from app.services.sessions import create_weekly_session


@pytest.mark.asyncio
async def test_create_weekly_session_integration(db_session):
    """Integration test for creating a weekly session.

    Note: DATABASE_URL is set to test database in conftest.py before
     any imports,
    so create_weekly_session will use the test database automatically.
    """
    from sqlalchemy import select

    session = await create_weekly_session()

    assert session is not None
    assert session.status == SessionStatus.OPEN
    assert session.date > datetime.now(UTC)
    assert session.registration_deadline < session.date
    assert (session.date - session.registration_deadline).days == 1

    result = await db_session.execute(select(Session).where(Session.id == session.id))
    db_session_obj = result.scalar_one_or_none()
    assert db_session_obj is not None
    assert db_session_obj.status == SessionStatus.OPEN
