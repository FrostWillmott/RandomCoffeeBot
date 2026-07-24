"""Unit tests for scheduler background jobs."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.enums import SessionStatus
from app.scheduler import (
    create_and_announce_session,
    match_and_notify,
    recover_unannounced_sessions,
    recover_unnotified_matched_sessions,
    shutdown_scheduler,
    start_scheduler,
)


def make_session_maker(db_session):
    """Build a mock async_session_maker whose context manager yields db_session."""
    maker = MagicMock()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=db_session)
    cm.__aexit__ = AsyncMock(return_value=False)
    maker.return_value = cm
    return maker


def make_db_session():
    db_session = MagicMock()
    db_session.commit = AsyncMock()
    return db_session


class TestCreateAndAnnounceSession:
    @pytest.mark.asyncio
    async def test_creates_and_announces(self, bot):
        db_session = make_db_session()
        session = MagicMock(id=1, status=SessionStatus.OPEN)

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch(
                "app.scheduler.create_weekly_session",
                AsyncMock(return_value=session),
            ),
            patch(
                "app.scheduler.post_session_announcement",
                AsyncMock(return_value=True),
            ) as announce,
        ):
            await create_and_announce_session(bot)

        announce.assert_awaited_once()
        assert db_session.commit.await_count == 2

    @pytest.mark.asyncio
    async def test_skips_announcement_for_existing_session(self, bot):
        db_session = make_db_session()
        session = MagicMock(id=1, status=SessionStatus.CLOSED)

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch(
                "app.scheduler.create_weekly_session",
                AsyncMock(return_value=session),
            ),
            patch("app.scheduler.post_session_announcement", AsyncMock()) as announce,
        ):
            await create_and_announce_session(bot)

        announce.assert_not_awaited()
        db_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_failed_announcement_keeps_session(self, bot):
        db_session = make_db_session()
        session = MagicMock(id=1, status=SessionStatus.OPEN)

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch(
                "app.scheduler.create_weekly_session",
                AsyncMock(return_value=session),
            ),
            patch(
                "app.scheduler.post_session_announcement",
                AsyncMock(return_value=False),
            ),
        ):
            await create_and_announce_session(bot)

        # Only the session-creation commit happened, not the announcement one.
        assert db_session.commit.await_count == 1

    @pytest.mark.asyncio
    async def test_swallows_exceptions(self, bot):
        maker = make_session_maker(make_db_session())
        with (
            patch("app.scheduler.async_session_maker", maker),
            patch(
                "app.scheduler.create_weekly_session",
                AsyncMock(side_effect=RuntimeError("boom")),
            ),
        ):
            await create_and_announce_session(bot)


class TestRecoverUnannouncedSessions:
    @pytest.mark.asyncio
    async def test_no_sessions_noop(self, bot):
        db_session = make_db_session()
        repo = MagicMock()
        repo.get_open_unannounced_sessions = AsyncMock(return_value=[])

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch("app.scheduler.SessionRepository", return_value=repo),
            patch("app.scheduler.post_session_announcement", AsyncMock()) as announce,
        ):
            await recover_unannounced_sessions(bot)

        announce.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_retries_announcement(self, bot):
        db_session = make_db_session()
        sess_ok = MagicMock(id=1)
        sess_fail = MagicMock(id=2)
        repo = MagicMock()
        repo.get_open_unannounced_sessions = AsyncMock(return_value=[sess_ok, sess_fail])

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch("app.scheduler.SessionRepository", return_value=repo),
            patch(
                "app.scheduler.post_session_announcement",
                AsyncMock(side_effect=[True, False]),
            ),
        ):
            await recover_unannounced_sessions(bot)

        assert db_session.commit.await_count == 1


class TestMatchAndNotify:
    @pytest.mark.asyncio
    async def test_notifies_sessions_with_matches(self, bot):
        db_session = make_db_session()
        results = [
            MagicMock(session_id=1, matches_created=2),
            MagicMock(session_id=2, matches_created=0),
        ]

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch(
                "app.scheduler.run_matching_for_closed_sessions",
                AsyncMock(return_value=results),
            ),
            patch(
                "app.scheduler.notify_all_matches_for_session",
                AsyncMock(return_value=True),
            ) as notify,
        ):
            await match_and_notify(bot)

        notify.assert_awaited_once()
        assert notify.await_args.args[1] == 1
        db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_no_commit_when_notification_fails(self, bot):
        db_session = make_db_session()
        results = [MagicMock(session_id=1, matches_created=1)]

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch(
                "app.scheduler.run_matching_for_closed_sessions",
                AsyncMock(return_value=results),
            ),
            patch(
                "app.scheduler.notify_all_matches_for_session",
                AsyncMock(return_value=False),
            ),
        ):
            await match_and_notify(bot)

        db_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_swallows_exceptions(self, bot):
        with patch(
            "app.scheduler.run_matching_for_closed_sessions",
            AsyncMock(side_effect=RuntimeError("boom")),
        ):
            await match_and_notify(bot)


class TestRecoverUnnotifiedMatchedSessions:
    @pytest.mark.asyncio
    async def test_no_sessions_noop(self, bot):
        db_session = make_db_session()
        repo = MagicMock()
        repo.get_matched_not_notified_sessions = AsyncMock(return_value=[])

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch("app.scheduler.SessionRepository", return_value=repo),
            patch("app.scheduler.notify_all_matches_for_session", AsyncMock()) as notify,
        ):
            await recover_unnotified_matched_sessions(bot)

        notify.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_retries_notifications(self, bot):
        db_session = make_db_session()
        sess_ok = MagicMock(id=1)
        sess_fail = MagicMock(id=2)
        repo = MagicMock()
        repo.get_matched_not_notified_sessions = AsyncMock(
            return_value=[sess_ok, sess_fail]
        )

        with (
            patch("app.scheduler.async_session_maker", make_session_maker(db_session)),
            patch("app.scheduler.SessionRepository", return_value=repo),
            patch(
                "app.scheduler.notify_all_matches_for_session",
                AsyncMock(side_effect=[True, False]),
            ),
        ):
            await recover_unnotified_matched_sessions(bot)

        assert db_session.commit.await_count == 1


class TestSchedulerLifecycle:
    @pytest.mark.asyncio
    async def test_start_scheduler(self):
        scheduler = MagicMock()
        await start_scheduler(scheduler)
        scheduler.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_scheduler_raises_on_failure(self):
        scheduler = MagicMock()
        scheduler.start.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError):
            await start_scheduler(scheduler)

    @pytest.mark.asyncio
    async def test_shutdown_running_scheduler(self):
        scheduler = MagicMock(running=True)
        await shutdown_scheduler(scheduler)
        scheduler.shutdown.assert_called_once_with(wait=True)

    @pytest.mark.asyncio
    async def test_shutdown_stopped_scheduler(self):
        scheduler = MagicMock(running=False)
        await shutdown_scheduler(scheduler)
        scheduler.shutdown.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown_swallows_errors(self):
        scheduler = MagicMock(running=True)
        scheduler.shutdown.side_effect = RuntimeError("boom")
        await shutdown_scheduler(scheduler)
