"""Scheduler module for background tasks."""

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-untyped]
)
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.exc import SQLAlchemyError

from app.constants import (
    MATCHING_CHECK_MINUTE,
    REGISTRATION_CLOSE_CHECK_MINUTE,
    SESSION_CREATION_DAY,
    SESSION_CREATION_HOUR,
    SESSION_CREATION_MINUTE,
)
from app.db.session import async_session_maker
from app.models.enums import SessionStatus
from app.repositories.match import MatchRepository
from app.repositories.registration import RegistrationRepository
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository
from app.services.announcements import post_session_announcement
from app.services.matching import (
    close_registration_for_expired_sessions,
    run_matching_for_closed_sessions,
)
from app.services.notifications import notify_all_matches_for_session
from app.services.sessions import create_weekly_session

logger = logging.getLogger(__name__)


async def create_and_announce_session(bot: Bot) -> None:
    """Create a new session and post an announcement to the channel.

    The session is committed BEFORE the announcement attempt so that
    a failed announcement does not lose the session. The session stays
    OPEN with announcement_message_id = NULL and a recovery job picks
    it up later.
    """
    try:
        async with async_session_maker() as db_session:
            session_repo = SessionRepository(db_session)

            logger.info("Creating weekly session...")
            session = await create_weekly_session(session_repo)

            if session.status != SessionStatus.OPEN:
                logger.warning(
                    f"Session {session.id} already exists with status "
                    f"'{session.status}'. Skipping announcement."
                )
                return

            # Commit session first — don't lose it if announcement fails.
            await db_session.commit()
            logger.info(f"Session {session.id} created and committed")

        # Post announcement in a separate DB session so failure
        # cannot roll back the session creation.
        async with async_session_maker() as db_session:
            session_repo = SessionRepository(db_session)
            logger.info(f"Posting announcement for session {session.id}...")
            success = await post_session_announcement(bot, session, session_repo)
            if success:
                await db_session.commit()
                logger.info(f"Session {session.id} announced successfully")
            else:
                logger.error(
                    f"Failed to post announcement for session {session.id} "
                    f"— session exists but is unannounced"
                )

    except SQLAlchemyError as e:
        logger.exception("Database error in create_and_announce_session", exc_info=e)
    except Exception as e:
        logger.exception("Error in create_and_announce_session", exc_info=e)


async def recover_unannounced_sessions(bot: Bot) -> None:
    """Recover sessions that were created but never announced.

    Runs periodically to catch sessions where announcement failed
    (e.g. Telegram was down, process crashed between create and announce).
    """
    try:
        async with async_session_maker() as db_session:
            session_repo = SessionRepository(db_session)
            sessions = await session_repo.get_open_unannounced_sessions()

            if not sessions:
                return

            logger.info(f"Found {len(sessions)} unannounced session(s), retrying...")
            for sess in sessions:
                logger.info(
                    f"Retrying announcement for session {sess.id} (date: {sess.date})"
                )
                success = await post_session_announcement(bot, sess, session_repo)
                if success:
                    await db_session.commit()
                    logger.info(f"Recovered announcement for session {sess.id}")
                else:
                    logger.error(f"Still could not announce session {sess.id}")

    except SQLAlchemyError as e:
        logger.exception("Database error in recover_unannounced_sessions", exc_info=e)
    except Exception as e:
        logger.exception("Error in recover_unannounced_sessions", exc_info=e)


async def match_and_notify(bot: Bot) -> None:
    """Run matching for closed sessions, then send notifications.

    Orchestrates matching (pure data) and notification (Telegram API)
    as separate concerns.
    """
    try:
        results = await run_matching_for_closed_sessions()

        for result in results:
            if result.matches_created > 0:
                logger.info(f"Posting matches to group for session {result.session_id}...")
                async with async_session_maker() as db_session:
                    match_repo = MatchRepository(db_session)
                    user_repo = UserRepository(db_session)
                    session_repo = SessionRepository(db_session)
                    reg_repo = RegistrationRepository(db_session)
                    success = await notify_all_matches_for_session(
                        bot,
                        result.session_id,
                        match_repo,
                        user_repo,
                        session_repo,
                        reg_repo,
                    )
                    if success:
                        await db_session.commit()
                logger.info(f"Posted matches for session {result.session_id}: {success}")

    except Exception as e:
        logger.exception("Error in match_and_notify", exc_info=e)


async def recover_unnotified_matched_sessions(bot: Bot) -> None:
    """Recover matched sessions whose notifications were never sent.

    Covers the gap between committing matches and sending notifications:
    if the process crashes between, this recovery job picks up unmatched
    MATCHED sessions.
    """
    try:
        async with async_session_maker() as db_session:
            session_repo = SessionRepository(db_session)
            sessions = await session_repo.get_matched_not_notified_sessions()

            if not sessions:
                return

            logger.info(f"Found {len(sessions)} unnotified matched session(s), retrying...")
            for sess in sessions:
                logger.info(f"Retrying notifications for session {sess.id}")
                match_repo = MatchRepository(db_session)
                user_repo = UserRepository(db_session)
                reg_repo = RegistrationRepository(db_session)
                success = await notify_all_matches_for_session(
                    bot,
                    sess.id,
                    match_repo,
                    user_repo,
                    session_repo,
                    reg_repo,
                )
                if success:
                    await db_session.commit()
                    logger.info(f"Recovered notifications for session {sess.id}")
                else:
                    logger.error(f"Still could not notify for session {sess.id}")

    except SQLAlchemyError as e:
        logger.exception(
            "Database error in recover_unnotified_matched_sessions", exc_info=e
        )
    except Exception as e:
        logger.exception("Error in recover_unnotified_matched_sessions", exc_info=e)


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
        match_and_notify,
        CronTrigger(minute=MATCHING_CHECK_MINUTE, timezone="UTC"),
        args=[bot],
        id="run_matching",
        replace_existing=True,
    )

    scheduler.add_job(
        recover_unannounced_sessions,
        CronTrigger(minute=30, timezone="UTC"),
        args=[bot],
        id="recover_announcements",
        replace_existing=True,
    )

    scheduler.add_job(
        recover_unnotified_matched_sessions,
        CronTrigger(minute=45, timezone="UTC"),
        args=[bot],
        id="recover_notifications",
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
        logger.exception("Failed to start scheduler", exc_info=e)
        raise


async def shutdown_scheduler(scheduler: AsyncIOScheduler):
    """Shutdown the scheduler gracefully."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.exception("Error stopping scheduler", exc_info=e)
