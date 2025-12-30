"""Unit tests for notifications service with a mocked database."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

from app.models.match import Match
from app.models.session import Session
from app.models.topic import Topic
from app.models.user import User
from app.services.notifications import (
    _create_match_keyboard,
    _create_match_message,
    _format_user_info,
    mark_user_inactive,
)


@pytest.mark.asyncio
async def test_format_user_info_full():
    """Test formatting user info with all fields."""
    user = User(
        telegram_id=1002,
        username="fulluser",
        first_name="First",
        last_name="Last",
        is_active=True,
    )

    info = _format_user_info(user)
    assert "First" in info
    assert "Last" in info
    assert "@fulluser" in info


@pytest.mark.asyncio
async def test_format_user_info_minimal():
    """Test formatting user info with minimal fields."""
    user = User(telegram_id=1003, is_active=True)

    info = _format_user_info(user)
    assert "User #1003" in info


@pytest.mark.asyncio
async def test_format_user_info_username_only():
    """Test formatting user info with only a username."""
    user = User(telegram_id=1004, username="usernameonly", is_active=True)

    info = _format_user_info(user)
    assert "@usernameonly" in info


@pytest.mark.asyncio
async def test_create_match_keyboard():
    """Test creating match keyboard."""
    keyboard = _create_match_keyboard(123)

    assert keyboard is not None
    assert len(keyboard.inline_keyboard) == 2
    assert keyboard.inline_keyboard[0][0].callback_data == "confirm_match:123"
    assert keyboard.inline_keyboard[1][0].callback_data == "suggest_time:123"


@pytest.mark.asyncio
async def test_create_match_message():
    """Test creating a match message."""
    user1 = User(telegram_id=2001, username="user1", first_name="User", is_active=True)
    user2 = User(telegram_id=2002, username="user2", first_name="Partner", is_active=True)
    topic = Topic(
        id=1,
        title="Test Topic",
        description="Test description",
        category="test",
        difficulty="middle",
        questions=["Q1", "Q2"],
        resources=[],
        is_active=True,
    )
    session = Session(
        id=1,
        date=datetime.now(UTC) + timedelta(days=5),
        registration_deadline=datetime.now(UTC) + timedelta(days=4),
        status="open",
        created_at=datetime.now(UTC),
    )
    match = Match(
        id=1,
        user1=user1,
        user2=user2,
        topic=topic,
        session=session,
        status="created",
        created_at=datetime.now(UTC),
    )

    message = _create_match_message(user1, user2, match)

    assert "Partner" in message or "@user2" in message
    assert "Test Topic" in message
    assert "Q1" in message or "Q2" in message


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
async def test_send_unmatched_notification_success():
    """Test sending unmatched notification successfully."""
    user_id = 4001
    telegram_id = 4001

    with patch(
        "app.services.notifications.async_session_maker"
    ) as mock_session_maker, patch("app.services.notifications.Bot") as mock_bot_class:
        mock_session = AsyncMock()
        mock_user = User(
            id=user_id, telegram_id=telegram_id, username="test", is_active=True
        )
        mock_session.get = AsyncMock(return_value=mock_user)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(return_value=MagicMock())
        mock_bot_class.return_value = mock_bot

        from app.services.notifications import send_unmatched_notification

        result = await send_unmatched_notification(mock_bot, user_id)

        assert result is True
        mock_bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_unmatched_notification_forbidden():
    """Test handling TelegramForbiddenError."""
    user_id = 4002
    telegram_id = 4002

    with patch(
        "app.services.notifications.async_session_maker"
    ) as mock_session_maker, patch(
        "app.services.notifications.mark_user_inactive"
    ) as mock_mark_inactive:
        mock_session = AsyncMock()
        mock_user = User(
            id=user_id, telegram_id=telegram_id, username="blocked", is_active=True
        )
        mock_session.get = AsyncMock(return_value=mock_user)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(
            side_effect=TelegramForbiddenError(
                method="sendMessage", message="Forbidden: bot was blocked by the user"
            )
        )

        from app.services.notifications import send_unmatched_notification

        result = await send_unmatched_notification(mock_bot, user_id)

        assert result is False
        mock_mark_inactive.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_send_unmatched_notification_user_not_found():
    """Test sending unmatched notification to a non-existent user."""
    user_id = 99999

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()

        from app.services.notifications import send_unmatched_notification

        result = await send_unmatched_notification(mock_bot, user_id)

        assert result is False
        mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_unmatched_notification_chat_not_found():
    """Test handling chat didn't found error."""
    user_id = 4003
    telegram_id = 4003

    with patch(
        "app.services.notifications.async_session_maker"
    ) as mock_session_maker, patch(
        "app.services.notifications.mark_user_inactive"
    ) as mock_mark_inactive:
        mock_session = AsyncMock()
        mock_user = User(
            id=user_id, telegram_id=telegram_id, username="notfound", is_active=True
        )
        mock_session.get = AsyncMock(return_value=mock_user)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(
            side_effect=TelegramAPIError(
                method="sendMessage", message="Bad Request: chat not found"
            )
        )

        from app.services.notifications import send_unmatched_notification

        result = await send_unmatched_notification(mock_bot, user_id)

        assert result is False
        mock_mark_inactive.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_send_match_notification_success():
    """Test sending match notification successfully."""
    match_id = 5001

    user1 = User(
        id=1, telegram_id=5001, username="user1", first_name="User1", is_active=True
    )
    user2 = User(
        id=2, telegram_id=5002, username="user2", first_name="User2", is_active=True
    )
    topic = Topic(
        id=1,
        title="Topic",
        description="Desc",
        category="test",
        difficulty="middle",
        questions=["Q1"],
        resources=[],
        is_active=True,
    )
    session = Session(
        id=1,
        date=datetime.now(UTC),
        registration_deadline=datetime.now(UTC),
        status="open",
        created_at=datetime.now(UTC),
    )
    match = Match(
        id=match_id,
        user1=user1,
        user2=user2,
        topic=topic,
        session=session,
        status="created",
        created_at=datetime.now(UTC),
    )

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=match)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(return_value=MagicMock())

        from app.services.notifications import send_match_notification

        result = await send_match_notification(mock_bot, match_id)

        assert result is True
        assert mock_bot.send_message.call_count == 2


@pytest.mark.asyncio
async def test_send_match_notification_match_not_found():
    """Test sending match notification when match not found."""
    match_id = 99999

    with patch("app.services.notifications.async_session_maker") as mock_session_maker:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()

        from app.services.notifications import send_match_notification

        result = await send_match_notification(mock_bot, match_id)

        assert result is False
        mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_notify_all_matches_for_session():
    """Test notifying all matches for a session."""
    session_id = 6001

    match1 = Match(
        id=1,
        user1_id=1,
        user2_id=2,
        session_id=session_id,
        status="created",
        created_at=datetime.now(UTC),
    )
    match2 = Match(
        id=2,
        user1_id=3,
        user2_id=4,
        session_id=session_id,
        status="created",
        created_at=datetime.now(UTC),
    )

    with patch(
        "app.services.notifications.async_session_maker"
    ) as mock_session_maker, patch(
        "app.services.notifications.send_match_notification"
    ) as mock_send_match:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [match1, match2]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        mock_bot = AsyncMock()
        mock_send_match.return_value = True

        from app.services.notifications import notify_all_matches_for_session

        result = await notify_all_matches_for_session(mock_bot, session_id)

        assert result == 2
        assert mock_send_match.call_count == 2
