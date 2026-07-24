"""Unit tests for the application entry point."""

import asyncio
import signal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.main import (
    main,
    run_heartbeat,
    setup_signal_handlers,
    shutdown_event,
    shutdown_services,
)


@pytest.fixture
def restore_signal_handlers():
    saved = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
    yield
    for sig, handler in saved.items():
        signal.signal(sig, handler)
    shutdown_event.clear()


class TestSetupSignalHandlers:
    def test_handler_sets_shutdown_event(self, restore_signal_handlers):
        setup_signal_handlers()

        handler = signal.getsignal(signal.SIGTERM)
        assert callable(handler)
        assert not shutdown_event.is_set()

        handler(signal.SIGTERM, None)

        assert shutdown_event.is_set()
        assert signal.getsignal(signal.SIGINT) is handler


class TestRunHeartbeat:
    @pytest.mark.asyncio
    async def test_writes_heartbeat_file(self):
        write = AsyncMock()
        file_cm = MagicMock()
        file_cm.__aenter__ = AsyncMock(return_value=MagicMock(write=write))
        file_cm.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("app.main.aiofiles.open", MagicMock(return_value=file_cm)),
            patch(
                "app.main.asyncio.sleep",
                AsyncMock(side_effect=asyncio.CancelledError),
            ),
            pytest.raises(asyncio.CancelledError),
        ):
            await run_heartbeat()

        write.assert_awaited_once_with("ok")

    @pytest.mark.asyncio
    async def test_write_error_is_logged_and_loop_continues(self):
        with (
            patch(
                "app.main.aiofiles.open",
                MagicMock(side_effect=OSError("disk full")),
            ),
            patch(
                "app.main.asyncio.sleep",
                AsyncMock(side_effect=asyncio.CancelledError),
            ),
            pytest.raises(asyncio.CancelledError),
        ):
            await run_heartbeat()


def make_services():
    bot = MagicMock()
    bot.session.close = AsyncMock()
    dp = MagicMock()
    dp.stop_polling = AsyncMock()
    throttling_mw = MagicMock()
    throttling_mw.close = AsyncMock()
    return MagicMock(), bot, dp, throttling_mw


async def forever(*_args):
    await asyncio.Event().wait()


class TestShutdownServices:
    @pytest.mark.asyncio
    async def test_stops_all_services(self):
        scheduler, bot, dp, throttling_mw = make_services()
        heartbeat_task = asyncio.ensure_future(forever())
        polling_task = asyncio.ensure_future(forever())
        engine = MagicMock()
        engine.dispose = AsyncMock()

        with (
            patch("app.main.shutdown_scheduler", AsyncMock()) as stop_scheduler,
            patch("app.main.engine", engine),
        ):
            await shutdown_services(
                scheduler, bot, dp, heartbeat_task, throttling_mw, polling_task
            )

        dp.stop_polling.assert_awaited_once()
        assert polling_task.cancelled()
        assert heartbeat_task.cancelled()
        stop_scheduler.assert_awaited_once_with(scheduler)
        throttling_mw.close.assert_awaited_once()
        bot.session.close.assert_awaited_once()
        engine.dispose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exits_nonzero_on_polling_error(self):
        scheduler, bot, dp, throttling_mw = make_services()
        heartbeat_task = asyncio.ensure_future(forever())
        engine = MagicMock()
        engine.dispose = AsyncMock()

        with (
            patch("app.main.shutdown_scheduler", AsyncMock()),
            patch("app.main.engine", engine),
            pytest.raises(SystemExit),
        ):
            await shutdown_services(
                scheduler,
                bot,
                dp,
                heartbeat_task,
                throttling_mw,
                polling_task=None,
                polling_error=RuntimeError("polling died"),
            )

    @pytest.mark.asyncio
    async def test_cleanup_errors_are_swallowed(self):
        scheduler, bot, dp, throttling_mw = make_services()
        throttling_mw.close.side_effect = RuntimeError("redis down")
        bot.session.close.side_effect = RuntimeError("session error")
        heartbeat_task = asyncio.ensure_future(forever())
        engine = MagicMock()
        engine.dispose = AsyncMock(side_effect=RuntimeError("dispose error"))

        with (
            patch("app.main.shutdown_scheduler", AsyncMock()),
            patch("app.main.engine", engine),
        ):
            await shutdown_services(scheduler, bot, dp, heartbeat_task, throttling_mw)


class TestMain:
    @pytest.mark.asyncio
    async def test_shutdown_signal_stops_services(self):
        scheduler, bot, dp, throttling_mw = make_services()
        dp.start_polling = forever

        async def fake_shutdown(*args, **kwargs):
            for task in args + tuple(kwargs.values()):
                if isinstance(task, asyncio.Task) and not task.done():
                    task.cancel()

        with (
            patch("app.main.get_bot", AsyncMock(return_value=bot)),
            patch("app.main.get_dispatcher", return_value=(dp, throttling_mw)),
            patch("app.main.setup_scheduler", return_value=scheduler),
            patch("app.main.start_scheduler", AsyncMock()) as start,
            patch("app.main.run_heartbeat", forever),
            patch(
                "app.main.shutdown_services", AsyncMock(side_effect=fake_shutdown)
            ) as shutdown,
        ):
            shutdown_event.set()
            try:
                await main()
            finally:
                shutdown_event.clear()

        start.assert_awaited_once_with(scheduler)
        shutdown.assert_awaited_once()
        assert shutdown.await_args.args[-1] is None  # no polling error

    @pytest.mark.asyncio
    async def test_polling_error_is_propagated_to_shutdown(self):
        scheduler, bot, dp, throttling_mw = make_services()
        error = RuntimeError("polling crashed")

        async def failing_polling(_bot):
            raise error

        dp.start_polling = failing_polling

        async def fake_shutdown(*args, **kwargs):
            for task in args + tuple(kwargs.values()):
                if isinstance(task, asyncio.Task) and not task.done():
                    task.cancel()

        with (
            patch("app.main.get_bot", AsyncMock(return_value=bot)),
            patch("app.main.get_dispatcher", return_value=(dp, throttling_mw)),
            patch("app.main.setup_scheduler", return_value=scheduler),
            patch("app.main.start_scheduler", AsyncMock()),
            patch("app.main.run_heartbeat", forever),
            patch(
                "app.main.shutdown_services", AsyncMock(side_effect=fake_shutdown)
            ) as shutdown,
        ):
            await main()

        assert shutdown.await_args.args[-1] is error
