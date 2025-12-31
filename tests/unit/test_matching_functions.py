"""Unit tests for matching service functions."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.enums import SessionStatus
from app.models.session import Session
from app.models.topic import Topic
from app.repositories.match import MatchRepository
from app.repositories.topic import TopicRepository
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

    # Mock TopicRepository
    mock_topic_repo = AsyncMock(spec=TopicRepository)
    mock_topic_repo.get_active_by_difficulty.return_value = [topic]
    mock_topic_repo.increment_usage.return_value = topic

    # Mock MatchRepository
    mock_match_repo = AsyncMock(spec=MatchRepository)
    mock_match_repo.get_topic_ids_used_by_users.return_value = set()

    with patch("app.services.matching.TopicRepository", return_value=mock_topic_repo):
        with patch("app.services.matching.MatchRepository", return_value=mock_match_repo):
            result = await select_topic_for_users(
                mock_topic_repo, mock_match_repo, user1_id, user2_id
            )

    assert result is not None
    assert result.id == topic.id
    mock_topic_repo.get_active_by_difficulty.assert_called_once_with("middle")
    mock_match_repo.get_topic_ids_used_by_users.assert_called_once_with(user1_id, user2_id)


@pytest.mark.asyncio
async def test_select_topic_for_users_no_topics():
    """Test selecting a topic when no topics available."""
    user1_id = 7003
    user2_id = 7004

    # Mock TopicRepository - no topics available
    mock_topic_repo = AsyncMock(spec=TopicRepository)
    mock_topic_repo.get_active_by_difficulty.return_value = []

    # Mock MatchRepository
    mock_match_repo = AsyncMock(spec=MatchRepository)
    mock_match_repo.get_topic_ids_used_by_users.return_value = set()

    result = await select_topic_for_users(
        mock_topic_repo, mock_match_repo, user1_id, user2_id
    )

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
