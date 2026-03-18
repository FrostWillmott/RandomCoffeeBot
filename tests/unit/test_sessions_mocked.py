"""Unit tests for sessions service with a mocked database."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.models.enums import SessionStatus
from app.models.session import Session
from app.services.sessions import create_weekly_session


@pytest.fixture
def mock_session_repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_weekly_session_new(mock_session_repo):
    """Test creating a new weekly session when one doesn't exist."""
    mock_session_repo.get_sessions_by_status.return_value = []
    mock_session_repo.get_by_date.return_value = None
    mock_session_repo.create.side_effect = lambda s: s

    result = await create_weekly_session(mock_session_repo)

    assert result is not None
    assert result.status == SessionStatus.OPEN
    mock_session_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_weekly_session_existing(mock_session_repo):
    """Test that creating a session for the same date returns an existing session."""
    now = datetime.now(UTC)
    future_date = now + timedelta(days=5)
    existing_session = Session(
        id=123,
        date=future_date,
        registration_deadline=future_date - timedelta(days=1),
        status=SessionStatus.OPEN,
        created_at=now,
    )
    mock_session_repo.get_sessions_by_status.return_value = []
    mock_session_repo.get_by_date.return_value = existing_session

    result = await create_weekly_session(mock_session_repo)

    assert result is not None
    assert result.id == 123
    mock_session_repo.create.assert_not_called()
