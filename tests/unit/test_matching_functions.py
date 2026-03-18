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
    create_matches_for_session,
    run_matching_for_closed_sessions,
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

    mock_topic_repo = AsyncMock(spec=TopicRepository)
    mock_topic_repo.get_active_by_difficulty.return_value = [topic]
    mock_topic_repo.increment_usage.return_value = topic

    mock_match_repo = AsyncMock(spec=MatchRepository)
    mock_match_repo.get_topic_ids_used_by_users.return_value = set()

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

    mock_topic_repo = AsyncMock(spec=TopicRepository)
    mock_topic_repo.get_active_by_difficulty.return_value = []

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

    with patch("app.services.matching.SessionRepository") as mock_session_repo_class:
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_id.return_value = None
        mock_session_repo_class.return_value = mock_session_repo

        mock_db_session = AsyncMock()

        result = await create_matches_for_session(session_id, db_session=mock_db_session)

        assert result == (0, [])


@pytest.mark.asyncio
async def test_run_matching_commits_before_notifications():
    """Test that run_matching_for_closed_sessions commits before notifications.

    Verifies the fix for transaction isolation issue where notifications
    couldn't see matches created in the same transaction before commit.
    """
    now = datetime.now(UTC)
    test_session = Session(
        id=1,
        date=now + timedelta(days=5),
        registration_deadline=now - timedelta(days=1),
        status=SessionStatus.CLOSED,
        created_at=now,
    )

    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(return_value=MagicMock())

    with patch("app.services.matching.async_session_maker") as mock_session_maker:
        with patch(
            "app.services.matching.create_matches_for_session"
        ) as mock_create_matches:
            with patch(
                "app.services.notifications.notify_all_matches_for_session"
            ) as mock_notify:
                mock_session = AsyncMock()

                mock_query_result = MagicMock()
                mock_query_result.scalars.return_value.all.return_value = [test_session]

                mock_update_result = MagicMock()
                mock_update_result.rowcount = 1

                mock_session.execute = AsyncMock(
                    side_effect=[mock_query_result, mock_update_result]
                )
                mock_session.commit = AsyncMock()
                mock_session.rollback = AsyncMock()
                mock_session.flush = AsyncMock()

                mock_session_maker.return_value.__aenter__.return_value = mock_session
                mock_session_maker.return_value.__aexit__.return_value = None

                mock_create_matches.return_value = (1, [])
                mock_notify.return_value = True

                call_order = []

                def track_commit(*args, **kwargs):
                    call_order.append("commit")
                    return AsyncMock()

                def track_notify(*args, **kwargs):
                    call_order.append("notify")
                    return AsyncMock(return_value=True)

                mock_session.commit.side_effect = track_commit
                mock_notify.side_effect = track_notify

                await run_matching_for_closed_sessions(mock_bot)

                assert "commit" in call_order, "session.commit() should be called"
                assert "notify" in call_order, (
                    "notify_all_matches_for_session() should be called"
                )
                commit_index = call_order.index("commit")
                notify_index = call_order.index("notify")
                assert commit_index < notify_index, (
                    "session.commit() should be called BEFORE "
                    "notify_all_matches_for_session()"
                )

                mock_create_matches.assert_called_once()
                mock_notify.assert_called_once_with(
                    mock_bot, test_session.id, mock_session, []
                )
