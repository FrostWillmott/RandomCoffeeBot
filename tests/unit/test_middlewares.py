"""Unit tests for aiogram middlewares."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import SQLAlchemyError

from app.bot.middlewares.database import DatabaseMiddleware
from app.bot.middlewares.throttling import ThrottlingMiddleware


def make_throttling(redis):
    with patch("app.bot.middlewares.throttling.Redis") as redis_cls:
        redis_cls.from_url.return_value = redis
        return ThrottlingMiddleware()


def make_redis(set_result=True):
    redis = MagicMock()
    redis.set = AsyncMock(return_value=set_result)
    redis.aclose = AsyncMock()
    return redis


class TestThrottlingMiddleware:
    @pytest.mark.asyncio
    async def test_message_passes_when_not_throttled(self):
        mw = make_throttling(make_redis(set_result=True))
        event = MagicMock(spec=Message)
        event.from_user = MagicMock(id=111)
        handler = AsyncMock(return_value="ok")

        assert await mw(handler, event, {}) == "ok"
        handler.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_message_dropped_when_throttled(self):
        mw = make_throttling(make_redis(set_result=None))
        event = MagicMock(spec=Message)
        event.from_user = MagicMock(id=111)
        handler = AsyncMock()

        assert await mw(handler, event, {}) is None
        handler.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_throttled_callback_still_answered(self):
        mw = make_throttling(make_redis(set_result=None))
        event = MagicMock(spec=CallbackQuery)
        event.from_user = MagicMock(id=111)
        event.answer = AsyncMock()
        handler = AsyncMock()

        assert await mw(handler, event, {}) is None
        event.answer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_other_event_types_pass_through(self):
        redis = make_redis()
        mw = make_throttling(redis)
        handler = AsyncMock(return_value="ok")

        assert await mw(handler, MagicMock(), {}) == "ok"
        redis.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_event_without_user_passes(self):
        redis = make_redis()
        mw = make_throttling(redis)
        event = MagicMock(spec=Message)
        event.from_user = None
        handler = AsyncMock(return_value="ok")

        assert await mw(handler, event, {}) == "ok"
        redis.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_fails_open_when_redis_down(self):
        redis = make_redis()
        redis.set.side_effect = ConnectionError("redis down")
        mw = make_throttling(redis)
        event = MagicMock(spec=Message)
        event.from_user = MagicMock(id=111)
        handler = AsyncMock(return_value="ok")

        assert await mw(handler, event, {}) == "ok"

    @pytest.mark.asyncio
    async def test_close_is_idempotent(self):
        redis = make_redis()
        mw = make_throttling(redis)

        await mw.close()
        await mw.close()

        redis.aclose.assert_awaited_once()


def make_db_session(new=(), dirty=(), deleted=()):
    session = MagicMock()
    session.new = set(new)
    session.dirty = set(dirty)
    session.deleted = set(deleted)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


def make_session_maker(session):
    maker = MagicMock()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)
    maker.return_value = cm
    return maker


class TestDatabaseMiddleware:
    @pytest.mark.asyncio
    async def test_provides_session_and_commits_changes(self):
        session = make_db_session(new={object()})
        handler = AsyncMock(return_value="ok")
        data = {}

        with patch(
            "app.bot.middlewares.database.async_session_maker",
            make_session_maker(session),
        ):
            result = await DatabaseMiddleware()(handler, MagicMock(), data)

        assert result == "ok"
        assert data["session"] is session
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_commit_when_clean(self):
        session = make_db_session()
        handler = AsyncMock(return_value="ok")

        with patch(
            "app.bot.middlewares.database.async_session_maker",
            make_session_maker(session),
        ):
            await DatabaseMiddleware()(handler, MagicMock(), {})

        session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_rolls_back_on_database_error(self):
        session = make_db_session()
        handler = AsyncMock(side_effect=SQLAlchemyError("boom"))

        with (
            patch(
                "app.bot.middlewares.database.async_session_maker",
                make_session_maker(session),
            ),
            pytest.raises(SQLAlchemyError),
        ):
            await DatabaseMiddleware()(handler, MagicMock(), {})

        session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rolls_back_on_unexpected_error(self):
        session = make_db_session()
        handler = AsyncMock(side_effect=RuntimeError("boom"))

        with (
            patch(
                "app.bot.middlewares.database.async_session_maker",
                make_session_maker(session),
            ),
            pytest.raises(RuntimeError),
        ):
            await DatabaseMiddleware()(handler, MagicMock(), {})

        session.rollback.assert_awaited_once()
