"""Unit tests for announcements service with a mocked database."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.exceptions import TelegramAPIError

from app.models.enums import SessionStatus
from app.models.session import Session
from app.services.announcements import post_session_announcement


@pytest.mark.asyncio
async def test_post_session_announcement_success(bot):
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

    with patch(
        "app.services.announcements.async_session_maker"
    ) as mock_session_maker, patch("app.services.announcements.settings") as mock_settings:
        mock_settings.channel_id = "@test_channel"

        mock_db_session = AsyncMock()
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_db_session
        mock_session_maker.return_value.__aexit__.return_value = None

        result = await post_session_announcement(bot, session)

    assert result is True
    bot.send_message.assert_called_once()
    assert session.announcement_message_id == 12345


@pytest.mark.asyncio
async def test_post_session_announcement_telegram_error(bot):
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

    with patch("app.services.announcements.settings") as mock_settings:
        mock_settings.channel_id = "@test_channel"

        result = await post_session_announcement(bot, session)

    assert result is False
    bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_post_session_announcement_general_error(bot):
    """Test handling general exception when posting an announcement."""
    session = Session(
        id=3,
        date=datetime.now(UTC) + timedelta(days=5),
        registration_deadline=datetime.now(UTC) + timedelta(days=4),
        status=SessionStatus.OPEN,
        created_at=datetime.now(UTC),
    )

    bot.send_message = AsyncMock(side_effect=Exception("Unexpected error"))

    with patch("app.services.announcements.settings") as mock_settings:
        mock_settings.channel_id = "@test_channel"

        result = await post_session_announcement(bot, session)

    assert result is False
    bot.send_message.assert_called_once()
