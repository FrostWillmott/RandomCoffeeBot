"""Scheduler module for background tasks."""

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-untyped]
)
from apscheduler.triggers.cron import CronTrigger

from app.constants import (
    MATCHING_CHECK_MINUTE,
    REGISTRATION_CLOSE_CHECK_MINUTE,
    SESSION_CREATION_DAY,
    SESSION_CREATION_HOUR,
    SESSION_CREATION_MINUTE,
)
from app.services.announcements import post_session_announcement
from app.services.matching import (
    close_registration_for_expired_sessions,
    run_matching_for_closed_sessions,
)
from app.services.sessions import create_weekly_session

logger = logging.getLogger(__name__)


async def create_and_announce_session(bot: Bot) -> None:
    """Create a new session and post an announcement to the channel."""
    try:
        logger.info("Creating weekly session...")
        session = await create_weekly_session()

        if session:
            logger.info(f"Posting announcement for session {session.id}...")
            success = await post_session_announcement(bot, session)
            if success:
                logger.info("Session created and announced successfully")
            else:
                logger.error("Failed to post announcement")
        else:
            logger.warning("No new session created")

    except Exception as e:
        logger.exception(
            "Error in create_and_announce_session",
            exc_info=e,
        )


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Initialize and configure the scheduler."""
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        create_and_announce_session,
        CronTrigger(
            day_of_week=SESSION_CREATION_DAY,
            hour=SESSION_CREATION_HOUR,
            minute=SESSION_CREATION_MINUTE,
            timezone="UTC",
        ),
        args=[bot],
        id="create_weekly_session",
        replace_existing=True,
    )

    scheduler.add_job(
        close_registration_for_expired_sessions,
        CronTrigger(minute=REGISTRATION_CLOSE_CHECK_MINUTE, timezone="UTC"),
        id="close_registrations",
        replace_existing=True,
    )

    scheduler.add_job(
        run_matching_for_closed_sessions,
        CronTrigger(minute=MATCHING_CHECK_MINUTE, timezone="UTC"),
        args=[bot],
        id="run_matching",
        replace_existing=True,
    )

    logger.info("Scheduler configured with jobs:")
    logger.info(
        f"  - create_weekly_session: Every {SESSION_CREATION_DAY} "
        f"at {SESSION_CREATION_HOUR:02d}:{SESSION_CREATION_MINUTE:02d} UTC"
    )
    logger.info(
        f"  - close_registrations: Every hour at :{REGISTRATION_CLOSE_CHECK_MINUTE:02d}"
    )
    logger.info(f"  - run_matching: Every hour at :{MATCHING_CHECK_MINUTE:02d}")

    return scheduler


async def start_scheduler(scheduler: AsyncIOScheduler):
    """Start the scheduler."""
    try:
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.exception(
            "Failed to start scheduler",
            exc_info=e,
        )
        raise


async def shutdown_scheduler(scheduler: AsyncIOScheduler):
    """Shutdown the scheduler gracefully."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.exception(
            "Error stopping scheduler",
            exc_info=e,
        )
