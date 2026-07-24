"""Unit tests for match interaction handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.bot.handlers.matches import (
    confirm_match,
    suggest_time,
    verify_match_participant,
)
from app.models.enums import MatchStatus
from app.models.user import User
from app.repositories.match import MatchRepository
from app.repositories.user import UserRepository


def make_callback(data, user_id=111):
    callback = MagicMock()
    callback.data = data
    callback.from_user = MagicMock(id=user_id)
    callback.message = MagicMock()
    callback.message.edit_text = AsyncMock()
    callback.answer = AsyncMock()
    return callback


def make_match(status=MatchStatus.CREATED, user1_id=1, user2_id=2, user3_id=None):
    return MagicMock(
        id=5, status=status, user1_id=user1_id, user2_id=user2_id, user3_id=user3_id
    )


class TestVerifyMatchParticipant:
    @pytest.mark.asyncio
    async def test_participant(self):
        user = User(id=1, telegram_id=111, username="u", is_active=True)
        with patch.object(
            UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
        ):
            assert await verify_match_participant(MagicMock(), 111, make_match())

    @pytest.mark.asyncio
    async def test_non_participant(self):
        user = User(id=99, telegram_id=111, username="u", is_active=True)
        with patch.object(
            UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
        ):
            assert not await verify_match_participant(MagicMock(), 111, make_match())

    @pytest.mark.asyncio
    async def test_unknown_user(self):
        with patch.object(
            UserRepository, "get_by_telegram_id", AsyncMock(return_value=None)
        ):
            assert not await verify_match_participant(MagicMock(), 111, make_match())


class TestConfirmMatch:
    @pytest.mark.asyncio
    async def test_confirms_created_match(self):
        callback = make_callback("confirm_match:5")
        match = make_match()
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(MatchRepository, "get_by_id", AsyncMock(return_value=match)),
            patch.object(MatchRepository, "update", AsyncMock()) as update,
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
        ):
            await confirm_match(callback, MagicMock())

        assert match.status == MatchStatus.CONFIRMED
        assert match.confirmed_at is not None
        update.assert_awaited_once_with(match)
        callback.answer.assert_awaited_once_with("Пара подтверждена!")

    @pytest.mark.asyncio
    async def test_already_confirmed_match(self):
        callback = make_callback("confirm_match:5")
        match = make_match(status=MatchStatus.CONFIRMED)
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(MatchRepository, "get_by_id", AsyncMock(return_value=match)),
            patch.object(MatchRepository, "update", AsyncMock()) as update,
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
        ):
            await confirm_match(callback, MagicMock())

        update.assert_not_awaited()
        assert "подтверждена" in callback.message.edit_text.await_args.args[0]

    @pytest.mark.asyncio
    async def test_match_not_found(self):
        callback = make_callback("confirm_match:5")

        with patch.object(MatchRepository, "get_by_id", AsyncMock(return_value=None)):
            await confirm_match(callback, MagicMock())

        assert "не найдена" in callback.message.edit_text.await_args.args[0]

    @pytest.mark.asyncio
    async def test_non_participant_denied(self):
        callback = make_callback("confirm_match:5")

        with (
            patch.object(
                MatchRepository, "get_by_id", AsyncMock(return_value=make_match())
            ),
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=None)
            ),
        ):
            await confirm_match(callback, MagicMock())

        callback.answer.assert_awaited_once_with(
            "⛔ У вас нет доступа к этой паре", show_alert=True
        )
        callback.message.edit_text.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_invalid_callback_data(self):
        callback = make_callback("confirm_match:oops")

        await confirm_match(callback, MagicMock())

        callback.answer.assert_awaited_once_with("Неверный ID пары")

    @pytest.mark.asyncio
    async def test_missing_data(self):
        callback = make_callback(None)

        await confirm_match(callback, MagicMock())

        callback.answer.assert_awaited_once_with("Неверный ID пары")


class TestSuggestTime:
    @pytest.mark.asyncio
    async def test_shows_instructions(self):
        callback = make_callback("suggest_time:5")

        await suggest_time(callback)

        callback.message.edit_text.assert_awaited_once()
        callback.answer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_invalid_callback_data(self):
        callback = make_callback("suggest_time:oops")

        await suggest_time(callback)

        callback.answer.assert_awaited_once_with("Неверный запрос")
        callback.message.edit_text.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_missing_data(self):
        callback = make_callback(None)

        await suggest_time(callback)

        callback.answer.assert_awaited_once_with("Неверный запрос")
