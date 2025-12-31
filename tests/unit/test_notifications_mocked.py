"""Unit tests for notifications service with a mocked database."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.match import Match
from app.models.topic import Topic
from app.models.user import User
from app.services.notifications import (
    _build_matches_message,
    _format_user_mention,
    mark_user_inactive,
)


@pytest.mark.asyncio
async def test_format_user_mention_with_username():
    """Test formatting user mention with username."""
    user = User(
        telegram_id=1002,
        username="testuser",
        first_name="First",
        last_name="Last",
        is_active=True,
    )

    mention = _format_user_mention(user)
    assert mention == "@testuser"


@pytest.mark.asyncio
async def test_format_user_mention_without_username():
    """Test formatting user mention without a username (fallback to link)."""
    user = User(
        telegram_id=1003,
        first_name="First",
        is_active=True,
    )

    mention = _format_user_mention(user)
    assert "tg://user?id=1003" in mention
    assert "First" in mention


@pytest.mark.asyncio
async def test_format_user_mention_no_name_no_username():
    """Test formatting user mention with no name and no username."""
    user = User(telegram_id=1004, is_active=True)

    mention = _format_user_mention(user)
    assert "tg://user?id=1004" in mention
    assert "Участник" in mention


@pytest.mark.asyncio
async def test_build_matches_message_empty():
    """Test building message with no matches."""
    message = _build_matches_message([])
    assert "Нет пар" in message


@pytest.mark.asyncio
async def test_build_matches_message_with_matches():
    """Test building message with matches."""
    user1 = User(telegram_id=1, username="user1", first_name="User1", is_active=True)
    user2 = User(telegram_id=2, username="user2", first_name="User2", is_active=True)
    topic = Topic(
        id=1,
        title="Test Topic",
        description="Test desc",
        category="test",
        difficulty="middle",
        questions=[],
        resources=[],
        is_active=True,
    )
    match = MagicMock(spec=Match)
    match.user1 = user1
    match.user2 = user2
    match.topic = topic

    message = _build_matches_message([match])

    assert "@user1" in message
    assert "@user2" in message
    assert "Test Topic" in message
    assert "Пары Random Coffee" in message


@pytest.mark.asyncio
async def test_build_matches_message_with_unmatched():
    """Test building message with unmatched users."""
    user1 = User(telegram_id=1, username="user1", first_name="User1", is_active=True)
    user2 = User(telegram_id=2, username="user2", first_name="User2", is_active=True)
    unmatched = User(telegram_id=3, username="lonely", first_name="Lonely", is_active=True)

    match = MagicMock(spec=Match)
    match.user1 = user1
    match.user2 = user2
    match.topic = None

    message = _build_matches_message([match], [unmatched])

    assert "@user1" in message
    assert "@user2" in message
    assert "@lonely" in message
    assert "Без пары" in message


@pytest.mark.asyncio
async def test_mark_user_inactive_with_mock():
    """Test marking a user as inactive with a mocked session."""
    user_id = 3001

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()
        mock_user = User(id=user_id, telegram_id=3001, is_active=True)
        mock_session.get = AsyncMock(return_value=mock_user)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        await mark_user_inactive(user_id)

        mock_session.get.assert_called_once_with(User, user_id)
        assert mock_user.is_active is False
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_mark_user_inactive_user_not_found():
    """Test marking non-existent user as inactive."""
    user_id = 99999

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        # Should not raise an error
        await mark_user_inactive(user_id)

        mock_session.get.assert_called_once_with(User, user_id)
        mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_notify_all_matches_for_session_success():
    """Test posting all matches to group successfully."""
    session_id = 6001

    user1 = User(telegram_id=1, username="user1", first_name="User1", is_active=True)
    user2 = User(telegram_id=2, username="user2", first_name="User2", is_active=True)
    topic = MagicMock(spec=Topic)
    topic.title = "Test Topic"

    match = MagicMock(spec=Match)
    match.user1 = user1
    match.user2 = user2
    match.topic = topic

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()

        mock_matches_result = MagicMock()
        mock_matches_result.scalars.return_value.all.return_value = [match]
        mock_session.execute = AsyncMock(return_value=mock_matches_result)

        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(return_value=MagicMock())

        from app.services.notifications import notify_all_matches_for_session

        result = await notify_all_matches_for_session(mock_bot, session_id)

        assert result is True
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert "@user1" in call_args.kwargs["text"]
        assert "@user2" in call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_notify_all_matches_for_session_no_matches():
    """Test notification when no matches found."""
    session_id = 6002

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()

        from app.services.notifications import notify_all_matches_for_session

        result = await notify_all_matches_for_session(mock_bot, session_id)

        assert result is False
        mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_notify_all_matches_with_unmatched_users():
    """Test notification includes unmatched users."""
    session_id = 6003

    user1 = User(id=1, telegram_id=1, username="user1", first_name="User1", is_active=True)
    user2 = User(id=2, telegram_id=2, username="user2", first_name="User2", is_active=True)
    unmatched = User(
        id=3, telegram_id=3, username="lonely", first_name="Lonely", is_active=True
    )

    topic = MagicMock(spec=Topic)
    topic.title = "Test Topic"

    match = MagicMock(spec=Match)
    match.user1 = user1
    match.user2 = user2
    match.topic = topic

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        with patch("app.services.notifications.MatchRepository") as mock_match_repo_class:
            with patch("app.services.notifications.UserRepository") as mock_user_repo_class:
                mock_session = AsyncMock()

                # Mock MatchRepository
                mock_match_repo = AsyncMock()
                mock_match_repo.get_by_session_id_with_relations.return_value = [match]
                mock_match_repo_class.return_value = mock_match_repo

                # Mock UserRepository
                mock_user_repo = AsyncMock()
                mock_user_repo.get_by_id.return_value = unmatched
                mock_user_repo_class.return_value = mock_user_repo

                mock_session_maker.return_value.__aenter__.return_value = mock_session
                mock_session_maker.return_value.__aexit__.return_value = None

                mock_bot = AsyncMock()
                mock_bot.send_message = AsyncMock(return_value=MagicMock())

                from app.services.notifications import notify_all_matches_for_session

                result = await notify_all_matches_for_session(
                    mock_bot, session_id, unmatched_user_ids=[3]
                )

                assert result is True
                call_args = mock_bot.send_message.call_args
                message_text = call_args.kwargs["text"]
                assert "@lonely" in message_text
                assert "Без пары" in message_text
