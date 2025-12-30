"""Matching algorithm service."""

import logging
import random
from datetime import UTC, datetime

from aiogram import Bot
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import async_session_maker
from app.models.enums import MatchStatus, SessionStatus
from app.models.match import Match
from app.models.registration import Registration
from app.models.session import Session
from app.models.topic import Topic

logger = logging.getLogger(__name__)


async def get_previous_matches(session, user_ids: list[int]) -> set[tuple[int, int]]:
    """Fetch all pairs of users who have matched before."""
    if not user_ids:
        return set()

    stmt = select(Match.user1_id, Match.user2_id).where(
        or_(Match.user1_id.in_(user_ids), Match.user2_id.in_(user_ids))
    )
    result = await session.execute(stmt)

    existing_pairs = set()
    for row in result.all():
        if row[0] is not None and row[1] is not None:
            existing_pairs.add(tuple(sorted((row[0], row[1]))))

    return existing_pairs


async def select_topic_for_users(
    user1_id: int, user2_id: int, db_session: AsyncSession | None = None
) -> Topic | None:
    """Select a topic that neither user has discussed recently."""
    if db_session is None:
        async with async_session_maker() as session:
            return await _select_topic_for_users_logic(session, user1_id, user2_id)
    else:
        return await _select_topic_for_users_logic(db_session, user1_id, user2_id)


async def _select_topic_for_users_logic(
    session: AsyncSession, user1_id: int, user2_id: int
) -> Topic | None:
    """Core logic for selecting a topic."""
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

    result = await session.execute(
        select(Topic).where(
            and_(
                Topic.is_active.is_(True),
                Topic.difficulty == "middle",
            )
        )
    )
    all_topics_list: list[Topic] = list(result.scalars().all())

    available_topics: list[Topic] = [
        t for t in all_topics_list if t.id not in used_topic_ids
    ]

    if not available_topics:
        available_topics = list(all_topics_list)

    if not available_topics:
        logger.error("No topics available for matching!")
        return None

    available_topics.sort(key=lambda t: (t.times_used, random.random()))

    selected_topic = available_topics[0]

    selected_topic.times_used += 1
    session.add(selected_topic)
    await session.flush()
    await session.refresh(selected_topic)

    return selected_topic


async def create_matches_for_session(
    session_id: int, db_session: AsyncSession | None = None
) -> tuple[int, list[int]]:
    """Create random matches for a session.

    Returns:
        Tuple[int, list[int]]: (number of matches created,
         list of unmatched user_ids)
    """
    if db_session is None:
        async with async_session_maker() as session:
            try:
                result = await _create_matches_logic(session, session_id)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e
    else:
        return await _create_matches_logic(db_session, session_id)


async def _create_matches_logic(
    db_session: AsyncSession, session_id: int
) -> tuple[int, list[int]]:
    """Core logic for creating matches."""
    result = await db_session.execute(select(Session).where(Session.id == session_id))
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        logger.error(f"Session {session_id} not found")
        return 0, []

    reg_result = await db_session.execute(
        select(Registration)
        .options(selectinload(Registration.user))
        .where(Registration.session_id == session_id)
    )
    registrations: list[Registration] = list(reg_result.scalars().all())

    if len(registrations) < 2:
        logger.warning(
            f"Not enough registrations for session {session_id} (only {len(registrations)})"
        )
        return 0, [r.user_id for r in registrations]

    user_ids = [r.user_id for r in registrations]
    past_matches = await get_previous_matches(db_session, user_ids)

    pool = list(registrations)
    random.shuffle(pool)

    matches_to_create = []

    while len(pool) >= 2:
        u1 = pool.pop()

        partner = None
        partner_index = None
        for i, candidate in enumerate(pool):
            pair = tuple(sorted((u1.user_id, candidate.user_id)))
            if pair not in past_matches:
                partner = candidate
                partner_index = i
                break

        if partner is None and len(pool) > 0:
            partner = pool[0]
            partner_index = 0
            pair = tuple(sorted((u1.user_id, partner.user_id)))
            if pair in past_matches:
                logger.warning(
                    f"Creating match between users {u1.user_id} "
                    f"and {partner.user_id} despite previous meeting "
                    f"(no fresh matches available)"
                )

        if partner is not None and partner_index is not None:
            pool.pop(partner_index)
            topic = await select_topic_for_users(
                u1.user_id, partner.user_id, db_session=db_session
            )

            match = Match(
                session_id=session_id,
                user1_id=u1.user_id,
                user2_id=partner.user_id,
                topic_id=topic.id if topic else None,
                status=MatchStatus.CREATED,
                created_at=datetime.now(UTC),
            )
            matches_to_create.append(match)

    for m in matches_to_create:
        db_session.add(m)

    matches_count = len(matches_to_create)

    all_users = set(u for u in user_ids)
    actual_matched = set()
    for m in matches_to_create:
        actual_matched.add(m.user1_id)
        actual_matched.add(m.user2_id)

    unmatched_ids = list(all_users - actual_matched)

    if len(unmatched_ids) > 0:
        logger.info(
            f"Session {session_id}: {len(unmatched_ids)} users unmatched: {unmatched_ids}"
        )

    session_obj.status = SessionStatus.MATCHED
    db_session.add(session_obj)

    await db_session.flush()

    logger.info(f"Created {matches_count} matches for session {session_id}")
    return matches_count, unmatched_ids


async def run_matching_for_closed_sessions(bot: Bot) -> None:
    """Run matching for all sessions with closed registration."""
    from app.services.notifications import (
        notify_all_matches_for_session,
        send_unmatched_notification,
    )

    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(Session).where(
                    and_(
                        Session.status == SessionStatus.CLOSED,
                        Session.registration_deadline < datetime.now(UTC),
                    )
                )
            )
            sessions_to_match = result.scalars().all()

            for sess in sessions_to_match:
                logger.info(f"Running matching for session {sess.id}")
                (
                    matches_created,
                    unmatched_ids,
                ) = await create_matches_for_session(sess.id)
                logger.info(
                    f"Session {sess.id}: Created {matches_created} matches."
                    f" Unmatched: {len(unmatched_ids)}"
                )

                for user_id in unmatched_ids:
                    await send_unmatched_notification(bot, user_id)

                if matches_created > 0:
                    logger.info(f"Sending notifications for session {sess.id}...")
                    notifications_sent = await notify_all_matches_for_session(bot, sess.id)
                    logger.info(
                        f"Sent {notifications_sent} notifications for session {sess.id}"
                    )

        except Exception as e:
            logger.exception(
                "Error in run_matching_for_closed_sessions",
                exc_info=e,
            )
            raise


async def close_registration_for_expired_sessions() -> None:
    """Close registration for sessions past their deadline."""
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(Session).where(
                    and_(
                        Session.status == SessionStatus.OPEN,
                        Session.registration_deadline < datetime.now(UTC),
                    )
                )
            )
            sessions_to_close = result.scalars().all()

            for sess in sessions_to_close:
                sess.status = SessionStatus.CLOSED
                session.add(sess)
                logger.info(
                    f"Closed registration for session {sess.id} "
                    f"(deadline: {sess.registration_deadline})"
                )

            await session.commit()
            logger.info(f"Closed registration for {len(sessions_to_close)} sessions")

        except Exception as e:
            logger.exception(
                "Error closing registrations",
                exc_info=e,
            )
            await session.rollback()
            raise
