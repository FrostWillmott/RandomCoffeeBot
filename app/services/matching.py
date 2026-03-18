"""Matching algorithm service."""

import logging
import random
from datetime import UTC, datetime

from aiogram import Bot
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.enums import MatchStatus, SessionStatus
from app.models.match import Match
from app.models.topic import Topic
from app.repositories.match import MatchRepository
from app.repositories.registration import RegistrationRepository
from app.repositories.session import SessionRepository
from app.repositories.topic import TopicRepository

logger = logging.getLogger(__name__)


async def get_previous_matches(
    match_repo: MatchRepository, user_ids: list[int]
) -> set[tuple[int, int]]:
    """Fetch all pairs of users who have matched before.

    Args:
        match_repo: Match repository
        user_ids: List of user IDs

    Returns:
        Set of sorted user ID pairs
    """
    return await match_repo.get_previous_matches_for_users(user_ids)


async def select_topic_for_users(
    topic_repo: TopicRepository,
    match_repo: MatchRepository,
    *user_ids: int,
) -> Topic | None:
    """Select a topic that none of the users have discussed recently.

    Args:
        topic_repo: Topic repository
        match_repo: Match repository
        *user_ids: Variable number of user IDs (2 for pairs, 3 for triplets)

    Returns:
        Selected topic or None if no topics are available
    """
    if not user_ids:
        logger.error("No user IDs provided for topic selection")
        return None

    used_topic_ids = await match_repo.get_topic_ids_used_by_users(*user_ids)

    all_topics_list = await topic_repo.get_active_by_difficulty("middle")

    available_topics = [t for t in all_topics_list if t.id not in used_topic_ids]

    if not available_topics:
        available_topics = list(all_topics_list)

    if not available_topics:
        logger.error("No topics available for matching!")
        return None

    available_topics.sort(key=lambda t: (t.times_used, random.random()))

    selected_topic = available_topics[0]

    await topic_repo.increment_usage(selected_topic.id)

    return selected_topic


async def create_matches_for_session(
    session_id: int, db_session: AsyncSession | None = None
) -> tuple[int, list[int]]:
    """Create random matches for a session.

    Args:
        session_id: Session ID
        db_session: Optional database session

    Returns:
        Tuple of (number of matches created, list of unmatched user_ids)
    """
    if db_session is None:
        async with async_session_maker() as session:
            try:
                result = await _create_matches_logic(session, session_id)
                await session.commit()
                return result
            except SQLAlchemyError:
                await session.rollback()
                raise
    else:
        return await _create_matches_logic(db_session, session_id)


async def _create_matches_logic(
    db_session: AsyncSession, session_id: int
) -> tuple[int, list[int]]:
    """Core logic for creating matches.

    Args:
        db_session: Database session
        session_id: Session ID

    Returns:
        Tuple of (matches created, unmatched user IDs)
    """
    session_repo = SessionRepository(db_session)
    registration_repo = RegistrationRepository(db_session)
    match_repo = MatchRepository(db_session)
    topic_repo = TopicRepository(db_session)

    session_obj = await session_repo.get_by_id(session_id)

    if not session_obj:
        logger.error(f"Session {session_id} not found")
        return 0, []

    registrations = await registration_repo.get_by_session_id_with_users(session_id)

    if len(registrations) < 2:
        logger.warning(
            f"Not enough registrations for session {session_id} (only {len(registrations)})"
        )
        session_obj.status = SessionStatus.MATCHED
        await session_repo.update(session_obj)
        return 0, [r.user_id for r in registrations]

    user_ids = [r.user_id for r in registrations]
    past_matches = await get_previous_matches(match_repo, user_ids)

    pool = list(registrations)
    random.shuffle(pool)

    matches_to_create = []

    if len(pool) % 2 == 1 and len(pool) >= 3:
        u1 = pool.pop()
        u2 = pool.pop()
        u3 = pool.pop()

        best_combination = None
        best_score = -1

        for perm in [
            (u1, u2, u3),
            (u1, u3, u2),
            (u2, u1, u3),
            (u2, u3, u1),
            (u3, u1, u2),
            (u3, u2, u1),
        ]:
            p1, p2, p3 = perm
            pair12 = tuple(sorted((p1.user_id, p2.user_id)))
            pair13 = tuple(sorted((p1.user_id, p3.user_id)))
            pair23 = tuple(sorted((p2.user_id, p3.user_id)))

            score = 0
            if pair12 in past_matches:
                score += 1
            if pair13 in past_matches:
                score += 1
            if pair23 in past_matches:
                score += 1

            if score < best_score or best_score == -1:
                best_score = score
                best_combination = (p1, p2, p3)

        if best_combination:
            u1, u2, u3 = best_combination
            if best_score > 0:
                logger.warning(
                    f"Creating group of 3 with some previous matches: "
                    f"{u1.user_id}, {u2.user_id}, {u3.user_id}"
                )

            topic = await select_topic_for_users(
                topic_repo, match_repo, u1.user_id, u2.user_id, u3.user_id
            )

            match = Match(
                session_id=session_id,
                user1_id=u1.user_id,
                user2_id=u2.user_id,
                user3_id=u3.user_id,
                topic_id=topic.id if topic else None,
                status=MatchStatus.CREATED,
                created_at=datetime.now(UTC),
            )
            matches_to_create.append(match)
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
                topic_repo, match_repo, u1.user_id, partner.user_id
            )

            match = Match(
                session_id=session_id,
                user1_id=u1.user_id,
                user2_id=partner.user_id,
                user3_id=None,
                topic_id=topic.id if topic else None,
                status=MatchStatus.CREATED,
                created_at=datetime.now(UTC),
            )
            matches_to_create.append(match)

    for m in matches_to_create:
        await match_repo.create(m)

    matches_count = len(matches_to_create)

    all_users = set(u for u in user_ids)
    actual_matched = set()
    for m in matches_to_create:
        actual_matched.add(m.user1_id)
        actual_matched.add(m.user2_id)
        if m.user3_id:
            actual_matched.add(m.user3_id)

    unmatched_ids = list(all_users - actual_matched)

    if len(unmatched_ids) > 0:
        logger.info(
            f"Session {session_id}: {len(unmatched_ids)} users unmatched: {unmatched_ids}"
        )

    session_obj.status = SessionStatus.MATCHED
    await session_repo.update(session_obj)

    logger.info(f"Created {matches_count} matches for session {session_id}")
    return matches_count, unmatched_ids


async def run_matching_for_closed_sessions(bot: Bot) -> None:
    """Run matching for all sessions with closed registration.

    Args:
        bot: Bot instance for sending notifications
    """
    from app.services.notifications import notify_all_matches_for_session

    async with async_session_maker() as session:
        try:
            session_repo = SessionRepository(session)
            sessions_to_match = await session_repo.get_closed_sessions_ready_for_matching(
                datetime.now(UTC)
            )

            for sess in sessions_to_match:
                claimed = await session_repo.claim_for_matching(sess.id)
                if not claimed:
                    logger.info(f"Session {sess.id} already being processed, skipping")
                    continue

                await session.flush()

                logger.info(f"Running matching for session {sess.id}")
                matches_created, unmatched_ids = await create_matches_for_session(
                    sess.id, db_session=session
                )
                logger.info(
                    f"Session {sess.id}: Created {matches_created} matches."
                    f" Unmatched: {len(unmatched_ids)}"
                )

                await session.commit()

                if matches_created > 0:
                    logger.info(f"Posting matches to group for session {sess.id}...")
                    success = await notify_all_matches_for_session(
                        bot, sess.id, unmatched_ids
                    )
                    logger.info(f"Posted matches for session {sess.id}: {success}")

        except SQLAlchemyError as e:
            logger.exception("Error in run_matching_for_closed_sessions", exc_info=e)
            await session.rollback()
            raise


async def close_registration_for_expired_sessions() -> None:
    """Close registration for sessions past their deadline."""
    async with async_session_maker() as session:
        try:
            session_repo = SessionRepository(session)
            sessions_to_close = await session_repo.get_expired_open_sessions(
                datetime.now(UTC)
            )

            for sess in sessions_to_close:
                sess.status = SessionStatus.CLOSED
                await session_repo.update(sess)
                logger.info(
                    f"Closed registration for session {sess.id} "
                    f"(deadline: {sess.registration_deadline})"
                )

            await session.commit()
            logger.info(f"Closed registration for {len(sessions_to_close)} sessions")

        except SQLAlchemyError as e:
            logger.exception("Error closing registrations", exc_info=e)
            await session.rollback()
            raise
