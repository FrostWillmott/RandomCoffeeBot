"""Unit tests for command handlers."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message

from app.bot.handlers.commands import (
    _format_status_message,
    cmd_help,
    cmd_status,
    handle_unknown_callback,
)
from app.models.enums import MatchStatus
from app.models.user import User
from app.repositories.match import MatchRepository
from app.repositories.registration import RegistrationRepository
from app.repositories.user import UserRepository


def make_message(user_id=111):
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(id=user_id)
    message.answer = AsyncMock()
    return message


def make_callback(user_id=111):
    callback = MagicMock(spec=CallbackQuery)
    callback.from_user = MagicMock(id=user_id)
    callback.message = MagicMock()
    callback.message.edit_text = AsyncMock()
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()
    return callback


class TestCmdHelp:
    @pytest.mark.asyncio
    async def test_message(self):
        message = make_message()
        await cmd_help(message)
        assert "Справка" in message.answer.await_args.args[0]

    @pytest.mark.asyncio
    async def test_callback(self):
        callback = make_callback()
        await cmd_help(callback)
        assert "Справка" in callback.message.edit_text.await_args.args[0]
        callback.answer.assert_awaited_once()


class TestFormatStatusMessage:
    def test_no_registrations_or_matches(self):
        user = User(id=1, telegram_id=111, first_name="Иван", is_active=True)
        text = _format_status_message(user, [], [])
        assert "Нет активных регистраций" in text

    def test_with_registrations_and_matches(self):
        user = User(id=1, telegram_id=111, first_name="Иван", is_active=True)
        sess = MagicMock(date=datetime(2026, 7, 27, tzinfo=UTC))
        match = MagicMock(status=MatchStatus.CONFIRMED)

        text = _format_status_message(user, [(MagicMock(), sess)], [(match, sess)])

        assert "Активные регистрации" in text
        assert "2026-07-27" in text
        assert "Подтверждена" in text


class TestCmdStatus:
    @pytest.mark.asyncio
    async def test_unregistered_user(self):
        message = make_message()

        with patch.object(
            UserRepository, "get_by_telegram_id", AsyncMock(return_value=None)
        ):
            await cmd_status(message, MagicMock())

        assert "не зарегистрированы" in message.answer.await_args.args[0]

    @pytest.mark.asyncio
    async def test_registered_user_via_message(self):
        message = make_message()
        user = User(id=1, telegram_id=111, first_name="Иван", is_active=True)

        with (
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
            patch.object(
                RegistrationRepository,
                "get_active_registrations_with_session",
                AsyncMock(return_value=[]),
            ),
            patch.object(
                MatchRepository,
                "get_active_matches_with_session",
                AsyncMock(return_value=[]),
            ),
        ):
            await cmd_status(message, MagicMock())

        assert "Ваш статус" in message.answer.await_args.args[0]

    @pytest.mark.asyncio
    async def test_registered_user_via_callback(self):
        callback = make_callback()
        user = User(id=1, telegram_id=111, first_name="Иван", is_active=True)

        with (
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
            patch.object(
                RegistrationRepository,
                "get_active_registrations_with_session",
                AsyncMock(return_value=[]),
            ),
            patch.object(
                MatchRepository,
                "get_active_matches_with_session",
                AsyncMock(return_value=[]),
            ),
        ):
            await cmd_status(callback, MagicMock())

        callback.message.edit_text.assert_awaited_once()
        callback.answer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_missing_user_noop(self):
        message = make_message()
        message.from_user = None

        with patch.object(UserRepository, "get_by_telegram_id", AsyncMock()) as get_user:
            await cmd_status(message, MagicMock())

        get_user.assert_not_awaited()
        message.answer.assert_not_awaited()


class TestHandleUnknownCallback:
    @pytest.mark.asyncio
    async def test_answers_and_shows_menu(self):
        callback = make_callback()

        await handle_unknown_callback(callback)

        callback.answer.assert_awaited_once()
        callback.message.answer.assert_awaited_once()
