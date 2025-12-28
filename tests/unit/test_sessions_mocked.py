"""Unit tests for sessions service with a mocked database."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.enums import SessionStatus
from app.models.session import Session
from app.services.sessions import create_weekly_session


@pytest.fixture
def mock_now():
    return datetime.now(UTC)


@pytest.fixture
def mock_datetime_patch(mock_now):
    with patch("app.services.sessions.datetime") as mock_dt:
        mock_dt.now.return_value = mock_now
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock_dt


@pytest.fixture
def mock_db_session():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    # Simulate DB assigning an ID
    mock_session.add.side_effect = lambda obj: setattr(obj, "id", 1)

    with patch("app.services.sessions.async_session_maker") as mock_maker:
        mock_maker.return_value.__aenter__.return_value = mock_session
        mock_maker.return_value.__aexit__.return_value = None
        yield mock_session


@pytest.mark.asyncio
async def test_create_weekly_session_new(mock_db_session, mock_datetime_patch, mock_now):
    """Test creating a new weekly session when one doesn't exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await create_weekly_session()

    assert result is not None
    assert result.status == SessionStatus.OPEN
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_weekly_session_existing(
    mock_db_session, mock_datetime_patch, mock_now
):
    """Test that creating a session for the same date returns an existing session."""
    future_date = mock_now + timedelta(days=5)
    existing_session = Session(
        id=123,
        date=future_date,
        registration_deadline=future_date - timedelta(days=1),
        status=SessionStatus.OPEN,
        created_at=mock_now,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_session
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await create_weekly_session()

    assert result is not None
    assert result.id == 123
    mock_db_session.add.assert_not_called()
