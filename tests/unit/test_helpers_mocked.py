"""Unit tests for helpers service with a mocked database."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.enums import SessionStatus
from app.models.session import Session
from app.models.user import User
from app.services.helpers import (
    get_active_user,
    get_next_open_session,
    get_user_by_telegram_id,
)


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_found():
    """Test getting user by telegram_id when found."""
    telegram_id = 8001
    user = User(id=1, telegram_id=telegram_id, username="test", is_active=True)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await get_user_by_telegram_id(mock_session, telegram_id)

    assert result is not None
    assert result.telegram_id == telegram_id
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_not_found():
    """Test getting user by telegram_id when not found."""
    telegram_id = 99999

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await get_user_by_telegram_id(mock_session, telegram_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_next_open_session_found():
    """Test getting next open session when found."""
    now = datetime.now(UTC)
    future_date = now + timedelta(days=5)

    session = Session(
        id=1,
        date=future_date,
        registration_deadline=future_date - timedelta(days=1),
        status=SessionStatus.OPEN,
        created_at=now,
    )

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = session
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await get_next_open_session(mock_session)

    assert result is not None
    assert result.id == session.id
    assert result.status == SessionStatus.OPEN


@pytest.mark.asyncio
async def test_get_next_open_session_not_found():
    """Test getting next open session when not found."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await get_next_open_session(mock_session)

    assert result is None


@pytest.mark.asyncio
async def test_get_active_user_found():
    """Test getting active user when found."""
    telegram_id = 9001
    user = User(id=1, telegram_id=telegram_id, username="active", is_active=True)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await get_active_user(mock_session, telegram_id)

    assert result is not None
    assert result.telegram_id == telegram_id
    assert result.is_active is True


@pytest.mark.asyncio
async def test_get_active_user_not_found():
    """Test getting active user when not found - should raise ValueError."""
    telegram_id = 99999

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(ValueError, match=f"User {telegram_id} not found"):
        await get_active_user(mock_session, telegram_id)


@pytest.mark.asyncio
async def test_get_active_user_inactive():
    """Test getting inactive user - should raise ValueError."""
    telegram_id = 9002
    user = User(id=2, telegram_id=telegram_id, username="inactive", is_active=False)

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(ValueError, match=f"User {telegram_id} is inactive"):
        await get_active_user(mock_session, telegram_id)
