"""Unit tests for feedback handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.bot.handlers.feedback import process_comment, process_rating, start_feedback
from app.models.user import User
from app.repositories.feedback import FeedbackRepository
from app.repositories.match import MatchRepository
from app.repositories.user import UserRepository


def make_callback(data, user_id=111):
    callback = MagicMock()
    callback.data = data
    callback.from_user = MagicMock(id=user_id)
    callback.message = MagicMock()
    callback.message.answer = AsyncMock()
    callback.message.edit_text = AsyncMock()
    callback.answer = AsyncMock()
    return callback


def make_state(data=None):
    state = MagicMock()
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.get_data = AsyncMock(return_value=data or {})
    state.clear = AsyncMock()
    return state


def make_match(match_id=5, user1_id=1, user2_id=2, user3_id=None):
    return MagicMock(id=match_id, user1_id=user1_id, user2_id=user2_id, user3_id=user3_id)


class TestStartFeedback:
    @pytest.mark.asyncio
    async def test_starts_feedback_for_participant(self):
        callback = make_callback("start_feedback:5")
        state = make_state()
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(
                MatchRepository, "get_by_id", AsyncMock(return_value=make_match())
            ),
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
        ):
            await start_feedback(callback, MagicMock(), state)

        state.update_data.assert_awaited_once_with(match_id=5)
        state.set_state.assert_awaited_once()
        callback.message.answer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_accepts_legacy_feedback_prefix(self):
        callback = make_callback("feedback:5")
        state = make_state()
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(
                MatchRepository, "get_by_id", AsyncMock(return_value=make_match())
            ),
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
        ):
            await start_feedback(callback, MagicMock(), state)

        state.update_data.assert_awaited_once_with(match_id=5)

    @pytest.mark.asyncio
    async def test_invalid_callback_data(self):
        callback = make_callback("start_feedback:not_a_number")
        state = make_state()

        await start_feedback(callback, MagicMock(), state)

        callback.answer.assert_awaited_once_with("Неверный ID пары")
        state.set_state.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_missing_data(self):
        callback = make_callback(None)
        state = make_state()

        await start_feedback(callback, MagicMock(), state)

        callback.answer.assert_awaited_once_with("Неверный ID пары")

    @pytest.mark.asyncio
    async def test_match_not_found(self):
        callback = make_callback("start_feedback:5")
        state = make_state()

        with patch.object(MatchRepository, "get_by_id", AsyncMock(return_value=None)):
            await start_feedback(callback, MagicMock(), state)

        callback.answer.assert_awaited_once_with("Пара не найдена")

    @pytest.mark.asyncio
    async def test_non_participant_denied(self):
        callback = make_callback("start_feedback:5")
        state = make_state()
        outsider = User(id=99, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(
                MatchRepository, "get_by_id", AsyncMock(return_value=make_match())
            ),
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=outsider)
            ),
        ):
            await start_feedback(callback, MagicMock(), state)

        callback.answer.assert_awaited_once_with(
            "⛔ У вас нет доступа к этой паре", show_alert=True
        )
        state.set_state.assert_not_awaited()


class TestProcessRating:
    @pytest.mark.asyncio
    async def test_valid_rating(self):
        callback = make_callback("rating:4")
        state = make_state()

        await process_rating(callback, state)

        state.update_data.assert_awaited_once_with(rating=4)
        state.set_state.assert_awaited_once()
        callback.message.edit_text.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_invalid_rating(self):
        callback = make_callback("rating:9")
        state = make_state()

        await process_rating(callback, state)

        callback.answer.assert_awaited_once_with("Неверная оценка")
        state.update_data.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_missing_data(self):
        callback = make_callback(None)
        state = make_state()

        await process_rating(callback, state)

        callback.answer.assert_awaited_once_with("Неверная оценка")


def make_message(text="Отличная встреча!", user_id=111):
    message = MagicMock()
    message.text = text
    message.from_user = MagicMock(id=user_id)
    message.answer = AsyncMock()
    return message


class TestProcessComment:
    @pytest.mark.asyncio
    async def test_saves_feedback_with_comment(self):
        message = make_message()
        state = make_state({"match_id": 5, "rating": 4})
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
            patch.object(FeedbackRepository, "exists", AsyncMock(return_value=False)),
            patch.object(FeedbackRepository, "create", AsyncMock()) as create,
        ):
            await process_comment(message, MagicMock(), state)

        feedback = create.await_args.args[0]
        assert feedback.match_id == 5
        assert feedback.rating == 4
        assert feedback.comment == "Отличная встреча!"
        state.clear.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skip_comment(self):
        message = make_message(text="/skip")
        state = make_state({"match_id": 5, "rating": 4})
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
            patch.object(FeedbackRepository, "exists", AsyncMock(return_value=False)),
            patch.object(FeedbackRepository, "create", AsyncMock()) as create,
        ):
            await process_comment(message, MagicMock(), state)

        assert create.await_args.args[0].comment is None

    @pytest.mark.asyncio
    async def test_missing_state_data(self):
        message = make_message()
        state = make_state({})

        await process_comment(message, MagicMock(), state)

        message.answer.assert_awaited_once()
        state.clear.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        message = make_message()
        state = make_state({"match_id": 5, "rating": 4})

        with patch.object(
            UserRepository, "get_by_telegram_id", AsyncMock(return_value=None)
        ):
            await process_comment(message, MagicMock(), state)

        assert "/start" in message.answer.await_args.args[0]
        state.clear.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_duplicate_feedback_rejected(self):
        message = make_message()
        state = make_state({"match_id": 5, "rating": 4})
        user = User(id=1, telegram_id=111, username="u", is_active=True)

        with (
            patch.object(
                UserRepository, "get_by_telegram_id", AsyncMock(return_value=user)
            ),
            patch.object(FeedbackRepository, "exists", AsyncMock(return_value=True)),
            patch.object(FeedbackRepository, "create", AsyncMock()) as create,
        ):
            await process_comment(message, MagicMock(), state)

        create.assert_not_awaited()
        state.clear.assert_awaited_once()
