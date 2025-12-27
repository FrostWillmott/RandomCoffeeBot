"""Main application entry point."""

import asyncio
import logging
import sys

import aiofiles

from app.bot import get_bot, get_dispatcher
from app.scheduler import setup_scheduler, shutdown_scheduler, start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    # Initialize Bot and Dispatcher
    bot = await get_bot()
    dp = get_dispatcher()

    # Initialize and start Scheduler
    scheduler = setup_scheduler()
    await start_scheduler(scheduler)

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(run_heartbeat())

    logger.info("Starting polling...")
    polling_error = None
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Polling error: {e}")
        polling_error = e
    finally:
        # Stop heartbeat
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        # Shutdown scheduler
        await shutdown_scheduler(scheduler)
        # Close bot session
        logger.info("Bot stopped")
        await bot.session.close()
        # Exit with error code if polling failed
        if polling_error is not None:
            sys.exit(1)


async def run_heartbeat():
    """Update heartbeat file periodically."""
    while True:
        try:
            async with aiofiles.open("/tmp/healthy", "w") as f:
                await f.write("ok")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
        await asyncio.sleep(15)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually")
