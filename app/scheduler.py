"""Scheduler module for background tasks."""

import logging

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-untyped]
)

logger = logging.getLogger(__name__)


def setup_scheduler() -> AsyncIOScheduler:
    """Initialize options for the scheduler."""
    scheduler = AsyncIOScheduler()

    # Example task
    # scheduler.add_job(
    #     some_function,
    #     CronTrigger(hour=10, minute=0),
    #     id="daily_match",
    #     replace_existing=True
    # )

    return scheduler


async def start_scheduler(scheduler: AsyncIOScheduler):
    """Start the scheduler."""
    try:
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise


async def shutdown_scheduler(scheduler: AsyncIOScheduler):
    """Shutdown the scheduler gracefully."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
