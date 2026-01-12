"""Main application entry point."""

import asyncio
import logging
import signal
import sys

import aiofiles

from app.bot import get_bot, get_dispatcher
from app.bot.middlewares.throttling import throttling_middleware
from app.config import get_settings
from app.db.session import engine
from app.scheduler import setup_scheduler, shutdown_scheduler, start_scheduler
from app.utils.logging import setup_logging

settings = get_settings()
setup_logging(settings.log_level, settings.log_format)
logger = logging.getLogger(__name__)

shutdown_event = asyncio.Event()


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""

    def signal_handler(signum: int, _frame) -> None:
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


async def shutdown_services(
    scheduler, bot, dp, heartbeat_task, polling_task=None, polling_error=None
):
    """Cleanly shut down all running services."""
    logger.info("Shutting down services...")

    if polling_task and not polling_task.done():
        logger.info("Stopping polling...")
        await dp.stop_polling()
        polling_task.cancel()
        try:
            await polling_task
        except (asyncio.CancelledError, Exception) as e:
            if not isinstance(e, asyncio.CancelledError):
                logger.warning(f"Error during polling shutdown: {e}")

    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass

    await shutdown_scheduler(scheduler)

    try:
        await throttling_middleware.close()
    except Exception as e:  # Catch all unexpected errors for logging
        logger.warning(f"Error closing throttling middleware Redis client: {e}")

    try:
        await bot.session.close()
        await engine.dispose()
    except Exception as e:  # Catch all unexpected errors for logging
        logger.warning(f"Error during resource cleanup: {e}")

    logger.info("Bot stopped")
    if polling_error:
        sys.exit(1)


async def main():
    """Main entry point."""
    setup_signal_handlers()

    bot = await get_bot()
    dp = get_dispatcher()
    scheduler = setup_scheduler(bot)
    await start_scheduler(scheduler)

    heartbeat_task = asyncio.create_task(run_heartbeat())
    polling_task = asyncio.create_task(dp.start_polling(bot))
    shutdown_trigger = asyncio.create_task(shutdown_event.wait())

    logger.info("Starting polling...")
    polling_error = None

    try:
        done, _ = await asyncio.wait(
            [polling_task, shutdown_trigger],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if polling_task in done:
            polling_error = polling_task.exception()
            if polling_error:
                logger.error("Polling stopped unexpectedly", exc_info=polling_error)
        else:
            logger.info("Shutdown signal received.")

    except Exception as e:  # Catch all unexpected errors for logging
        logger.exception("Unexpected error in main loop")
        polling_error = e
    finally:
        for task in [shutdown_trigger]:
            if not task.done():
                task.cancel()

        await shutdown_services(
            scheduler, bot, dp, heartbeat_task, polling_task, polling_error
        )


async def run_heartbeat():
    """Update heartbeat file periodically."""
    from app.config import get_settings

    heartbeat_settings = get_settings()
    while True:
        try:
            async with aiofiles.open(
                heartbeat_settings.healthcheck_heartbeat_file, "w"
            ) as f:
                await f.write("ok")
        except Exception as e:  # Catch all unexpected errors for logging
            logger.exception("Heartbeat error", exc_info=e)
        await asyncio.sleep(15)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually")
