"""Matching algorithm service."""

import logging
import random
from datetime import datetime

from aiogram import Bot
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.models.match import Match
from app.models.registration import Registration
from app.models.session import Session
from app.models.topic import Topic

logger = logging.getLogger(__name__)


async def select_topic_for_users(user1_id: int, user2_id: int) -> Topic | None:
    """Select a topic that neither user has discussed recently."""
    async with async_session_maker() as session:
        # Get topics that users have already discussed
        result = await session.execute(
            select(Match.topic_id).where(
                and_(
                    Match.topic_id.isnot(None),
                    (Match.user1_id.in_([user1_id, user2_id]))
                    | (Match.user2_id.in_([user1_id, user2_id])),
                )
            )
        )
        used_topic_ids = {row[0] for row in result.all()}

        # Get all active topics for "middle" level
        result = await session.execute(
            select(Topic).where(
                and_(
                    Topic.is_active.is_(True),
                    Topic.difficulty == "middle",
                )
            )
        )
        all_topics = result.scalars().all()

        # Filter out used topics
        available_topics = [
            t for t in all_topics if t.id not in used_topic_ids
        ]

        # If no unused topics, use all topics (they've discussed everything)
        if not available_topics:
            available_topics = all_topics

        if not available_topics:
            logger.error("No topics available for matching!")
            return None

        # Sort by least used topics first (for fairness)
        available_topics.sort(key=lambda t: (t.times_used, random.random()))

        # Select topic (weighted towards less-used topics)
        selected_topic = available_topics[0]

        # Update topic statistics
        selected_topic.times_used += 1
        session.add(selected_topic)
        await session.commit()
        await session.refresh(selected_topic)

        return selected_topic


async def create_matches_for_session(session_id: int) -> int:
    """Create random matches for a session.

    Returns the number of matches created.
    """
    async with async_session_maker() as db_session:
        try:
            # Get the session
            result = await db_session.execute(
                select(Session).where(Session.id == session_id)
            )
            session_obj = result.scalar_one_or_none()

            if not session_obj:
                logger.error(f"Session {session_id} not found")
                return 0

            # Get all registrations for this session
            result = await db_session.execute(
                select(Registration)
                .options(selectinload(Registration.user))
                .where(Registration.session_id == session_id)
            )
            registrations = list(result.scalars().all())

            if len(registrations) < 2:
                logger.warning(
                    f"Not enough registrations for session {session_id} "
                    f"(only {len(registrations)})"
                )
                return 0

            # Shuffle registrations for random pairing
            random.shuffle(registrations)

            # Create pairs
            matches_created = 0
            i = 0
            while i < len(registrations) - 1:
                reg1 = registrations[i]
                reg2 = registrations[i + 1]

                # Select a topic for this pair
                topic = await select_topic_for_users(
                    reg1.user_id, reg2.user_id
                )

                # Create match
                match = Match(
                    session_id=session_id,
                    user1_id=reg1.user_id,
                    user2_id=reg2.user_id,
                    topic_id=topic.id if topic else None,
                    status="created",
                    created_at=datetime.utcnow(),
                )
                db_session.add(match)
                matches_created += 1

                i += 2

            # If odd number of participants, last person is unpaired
            if len(registrations) % 2 == 1:
                logger.info(
                    f"Odd number of participants ({len(registrations)}), "
                    f"one user will not be matched"
                )

            # Update session status
            session_obj.status = "matched"
            db_session.add(session_obj)

            await db_session.commit()

            logger.info(
                f"Created {matches_created} matches for session {session_id}"
            )
            return matches_created

        except Exception as e:
            logger.error(
                f"Error creating matches for session {session_id}: {e}"
            )
            await db_session.rollback()
            raise


async def run_matching_for_closed_sessions(bot: Bot) -> None:
    """Run matching for all sessions with closed registration."""
    from app.services.notifications import notify_all_matches_for_session

    async with async_session_maker() as session:
        try:
            # Find sessions that are closed but not yet matched
            result = await session.execute(
                select(Session).where(
                    and_(
                        Session.status == "closed",
                        Session.registration_deadline < datetime.utcnow(),
                    )
                )
            )
            sessions_to_match = result.scalars().all()

            for sess in sessions_to_match:
                logger.info(f"Running matching for session {sess.id}")
                matches_created = await create_matches_for_session(sess.id)
                logger.info(
                    f"Session {sess.id}: Created {matches_created} matches"
                )

                # Send notifications to matched users
                if matches_created > 0:
                    logger.info(
                        f"Sending notifications for session {sess.id}..."
                    )
                    notifications_sent = await notify_all_matches_for_session(
                        bot, sess.id
                    )
                    logger.info(
                        f"Sent {notifications_sent} notifications "
                        f"for session {sess.id}"
                    )

        except Exception as e:
            logger.error(f"Error in run_matching_for_closed_sessions: {e}")
            raise


async def close_registration_for_expired_sessions() -> None:
    """Close registration for sessions past their deadline."""
    async with async_session_maker() as session:
        try:
            # Find sessions with expired registration
            result = await session.execute(
                select(Session).where(
                    and_(
                        Session.status == "open",
                        Session.registration_deadline < datetime.utcnow(),
                    )
                )
            )
            sessions_to_close = result.scalars().all()

            for sess in sessions_to_close:
                sess.status = "closed"
                session.add(sess)
                logger.info(
                    f"Closed registration for session {sess.id} "
                    f"(deadline: {sess.registration_deadline})"
                )

            await session.commit()
            logger.info(
                f"Closed registration for {len(sessions_to_close)} sessions"
            )

        except Exception as e:
            logger.error(f"Error closing registrations: {e}")
            await session.rollback()
            raise
