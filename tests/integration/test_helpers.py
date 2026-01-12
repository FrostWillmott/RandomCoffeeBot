"""Integration tests for helper functions."""

import pytest

from app.models.enums import SessionStatus
from app.services.helpers import (
    get_active_user,
    get_next_open_session,
    get_user_by_telegram_id,
)


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_integration(db_session, user_factory):
    """Test getting user by telegram_id from a real database."""
    user = await user_factory(username="test_user", telegram_id=12345)

    found_user = await get_user_by_telegram_id(db_session, 12345)

    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.telegram_id == 12345
    assert found_user.username == "test_user"


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_not_found(db_session):
    """Test getting non-existent user."""
    found_user = await get_user_by_telegram_id(db_session, 99999)
    assert found_user is None


@pytest.mark.asyncio
async def test_get_next_open_session_integration(db_session, session_factory):
    """Test getting the next open session from a real database."""
    await session_factory(days_ahead=10, status=SessionStatus.CLOSED)
    open_session = await session_factory(days_ahead=5, status=SessionStatus.OPEN)
    await session_factory(days_ahead=3, status=SessionStatus.MATCHED)
    found_session = await get_next_open_session(db_session)

    assert found_session is not None
    assert found_session.id == open_session.id
    assert found_session.status == SessionStatus.OPEN


@pytest.mark.asyncio
async def test_get_next_open_session_none(db_session, session_factory):
    """Test when no open sessions exist."""
    await session_factory(days_ahead=5, status=SessionStatus.CLOSED)
    await session_factory(days_ahead=3, status=SessionStatus.MATCHED)

    found_session = await get_next_open_session(db_session)
    assert found_session is None


@pytest.mark.asyncio
async def test_get_active_user_integration(db_session, user_factory):
    """Test getting active user from a real database."""
    active_user = await user_factory(username="active", is_active=True)
    await user_factory(username="inactive", is_active=False)

    found_user = await get_active_user(db_session, active_user.telegram_id)

    assert found_user is not None
    assert found_user.id == active_user.id
    assert found_user.is_active is True


@pytest.mark.asyncio
async def test_get_active_user_inactive(db_session, user_factory):
    """Test that inactive users raise ValueError."""
    inactive_user = await user_factory(username="inactive", is_active=False)

    with pytest.raises(ValueError, match="is inactive"):
        await get_active_user(db_session, inactive_user.telegram_id)


@pytest.mark.asyncio
async def test_get_active_user_not_found(db_session):
    """Test that non-existent user raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        await get_active_user(db_session, 99999)
