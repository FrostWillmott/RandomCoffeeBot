"""Unit tests for matching service functions."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.enums import SessionStatus
from app.models.session import Session
from app.models.topic import Topic
from app.services.matching import (
    close_registration_for_expired_sessions,
    select_topic_for_users,
)


@pytest.mark.asyncio
async def test_select_topic_for_users_with_session():
    """Test selecting a topic for users with session parameter."""
    user1_id = 7001
    user2_id = 7002

    topic = Topic(
        id=1,
        title="Test Topic",
        description="Test",
        category="test",
        difficulty="middle",
        questions=["Q1"],
        resources=[],
        is_active=True,
        times_used=0,
    )

    mock_session = AsyncMock()

    mock_result1 = MagicMock()
    mock_result1.all.return_value = []

    mock_result2 = MagicMock()
    mock_result2.scalars.return_value.all.return_value = [topic]

    call_count = [0]

    def mock_execute(query):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_result1
        else:
            return mock_result2

    mock_session.execute = AsyncMock(side_effect=mock_execute)
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await select_topic_for_users(user1_id, user2_id, db_session=mock_session)

    assert result is not None
    assert result.id == topic.id
    assert mock_session.execute.call_count >= 2


@pytest.mark.asyncio
async def test_select_topic_for_users_no_topics():
    """Test selecting a topic when no topics available."""
    user1_id = 7003
    user2_id = 7004

    mock_session = AsyncMock()

    mock_result1 = MagicMock()
    mock_result1.all.return_value = []

    mock_result2 = MagicMock()
    mock_result2.scalars.return_value.all.return_value = []
    call_count = [0]

    def mock_execute(query):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_result1
        else:
            return mock_result2

    mock_session.execute = AsyncMock(side_effect=mock_execute)

    result = await select_topic_for_users(user1_id, user2_id, db_session=mock_session)

    assert result is None


@pytest.mark.asyncio
async def test_close_registration_for_expired_sessions():
    """Test closing registration for expired sessions."""

    now = datetime.now(UTC)
    expired_date = now - timedelta(days=1)
    future_date = now + timedelta(days=1)

    expired_session = Session(
        id=1,
        date=future_date,
        registration_deadline=expired_date,
        status=SessionStatus.OPEN,
        created_at=now,
    )

    with patch("app.services.matching.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [expired_session]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        await close_registration_for_expired_sessions()

        assert expired_session.status == SessionStatus.CLOSED
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_close_registration_for_expired_sessions_no_sessions():
    """Test closing registration when no expired sessions."""
    with patch("app.services.matching.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        await close_registration_for_expired_sessions()

        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_matches_for_session_with_session():
    """Test create_matches_for_session with the provided session."""
    session_id = 10001

    with patch("app.services.matching._create_matches_logic") as mock_create_logic:
        mock_create_logic.return_value = (2, [])

        mock_db_session = AsyncMock()
        from app.services.matching import create_matches_for_session

        result = await create_matches_for_session(session_id, db_session=mock_db_session)

        assert result == (2, [])
        mock_create_logic.assert_called_once_with(mock_db_session, session_id)
