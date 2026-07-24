"""Unit tests for the /start handler."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.bot.handlers.start import cmd_start
from app.models.user import User
from app.repositories.user import UserRepository


def make_message():
    message = MagicMock()
    message.from_user = MagicMock(
        id=111, username="ivan", first_name="Иван", last_name=None
    )
    temp_msg = MagicMock()
    temp_msg.delete = AsyncMock()
    message.answer = AsyncMock(return_value=temp_msg)
    return message, temp_msg


def make_user(created_at):
    user = User(id=1, telegram_id=111, username="ivan", is_active=True)
    user.created_at = created_at
    return user


class TestCmdStart:
    @pytest.mark.asyncio
    async def test_new_user_gets_welcome(self):
        message, temp_msg = make_message()
        user = make_user(datetime.now(UTC))

        with (
            patch.object(UserRepository, "get_or_create", AsyncMock(return_value=user)),
            patch("app.bot.handlers.start.asyncio.sleep", AsyncMock()),
        ):
            await cmd_start(message, MagicMock())

        temp_msg.delete.assert_awaited_once()
        final_text = message.answer.await_args_list[-1].args[0]
        assert "Добро пожаловать" in final_text

    @pytest.mark.asyncio
    async def test_returning_user_gets_menu(self):
        message, _ = make_message()
        user = make_user(datetime.now(UTC) - timedelta(days=30))

        with (
            patch.object(UserRepository, "get_or_create", AsyncMock(return_value=user)),
            patch("app.bot.handlers.start.asyncio.sleep", AsyncMock()),
        ):
            await cmd_start(message, MagicMock())

        final_text = message.answer.await_args_list[-1].args[0]
        assert "С возвращением" in final_text

    @pytest.mark.asyncio
    async def test_temp_message_delete_failure_ignored(self):
        message, temp_msg = make_message()
        temp_msg.delete.side_effect = RuntimeError("already deleted")
        user = make_user(datetime.now(UTC) - timedelta(days=30))

        with (
            patch.object(UserRepository, "get_or_create", AsyncMock(return_value=user)),
            patch("app.bot.handlers.start.asyncio.sleep", AsyncMock()),
        ):
            await cmd_start(message, MagicMock())

        assert message.answer.await_count == 2

    @pytest.mark.asyncio
    async def test_missing_user_noop(self):
        message, _ = make_message()
        message.from_user = None

        with patch.object(UserRepository, "get_or_create", AsyncMock()) as get_or_create:
            await cmd_start(message, MagicMock())

        get_or_create.assert_not_awaited()
        message.answer.assert_not_awaited()
