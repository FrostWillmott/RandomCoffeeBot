"""Unit tests for announcements service with a mocked database."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.exceptions import TelegramAPIError

from app.models.enums import SessionStatus
from app.models.session import Session
from app.services.announcements import post_session_announcement


@pytest.fixture
def mock_session_repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_post_session_announcement_success(bot, mock_session_repo):
    """Test posting a session announcement successfully."""
    session = Session(
        id=1,
        date=datetime.now(UTC) + timedelta(days=5),
        registration_deadline=datetime.now(UTC) + timedelta(days=4),
        status=SessionStatus.OPEN,
        created_at=datetime.now(UTC),
    )

    mock_message = MagicMock()
    mock_message.message_id = 12345
    bot.send_message = AsyncMock(return_value=mock_message)

    with patch("app.services.announcements.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.channel_id = "@test_channel"
        mock_get_settings.return_value = mock_settings

        mock_session_repo.update.return_value = session

        result = await post_session_announcement(bot, session, mock_session_repo)

    assert result is True
    bot.send_message.assert_called_once()
    assert session.announcement_message_id == 12345


@pytest.mark.asyncio
async def test_post_session_announcement_telegram_error(bot, mock_session_repo):
    """Test handling TelegramAPIError when posting an announcement."""
    session = Session(
        id=2,
        date=datetime.now(UTC) + timedelta(days=5),
        registration_deadline=datetime.now(UTC) + timedelta(days=4),
        status=SessionStatus.OPEN,
        created_at=datetime.now(UTC),
    )

    bot.send_message = AsyncMock(
        side_effect=TelegramAPIError(
            method="sendMessage", message="Forbidden: bot is not a member of the channel"
        )
    )

    with patch("app.services.announcements.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.channel_id = "@test_channel"
        mock_get_settings.return_value = mock_settings

        result = await post_session_announcement(bot, session, mock_session_repo)

    assert result is False
    bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_post_session_announcement_general_error(bot, mock_session_repo):
    """Test handling TelegramAPIError subclass when posting an announcement."""
    session = Session(
        id=3,
        date=datetime.now(UTC) + timedelta(days=5),
        registration_deadline=datetime.now(UTC) + timedelta(days=4),
        status=SessionStatus.OPEN,
        created_at=datetime.now(UTC),
    )

    bot.send_message = AsyncMock(
        side_effect=TelegramAPIError(method="sendMessage", message="Network error")
    )

    with patch("app.services.announcements.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.channel_id = "@test_channel"
        mock_get_settings.return_value = mock_settings

        result = await post_session_announcement(bot, session, mock_session_repo)

    assert result is False
    bot.send_message.assert_called_once()
