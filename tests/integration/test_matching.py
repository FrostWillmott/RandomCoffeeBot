"""Integration tests for matching service."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models.enums import MatchStatus, SessionStatus
from app.models.match import Match
from app.models.registration import Registration
from app.models.session import Session
from app.models.topic import Topic
from app.models.user import User
from app.repositories.match import MatchRepository
from app.services.matching import (
    create_matches_for_session,
    get_previous_matches,
)


async def create_user(db_session, telegram_id: int, username: str) -> User:
    """Helper to create a user."""
    user = User(
        telegram_id=telegram_id,
        username=username,  # nosec - test data
        first_name=f"User {username}",  # nosec - test data
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def create_session(db_session, date: datetime) -> Session:
    """Helper to create a session."""
    new_session = Session(
        date=date,
        registration_deadline=date - timedelta(days=1),
        status=SessionStatus.CLOSED,
        created_at=datetime.now(UTC),
    )
    db_session.add(new_session)
    await db_session.commit()
    await db_session.refresh(new_session)
    return new_session


async def register_users(db_session, session_id: int, users: list[User]):
    """Helper to register multiple users for a session."""
    for user in users:
        db_session.add(Registration(user_id=user.id, session_id=session_id))
    await db_session.commit()


async def create_topic(db_session) -> Topic:
    """Helper to create a topic."""
    topic = Topic(
        title="Test Topic",
        description="Test description",
        category="test",
        difficulty="middle",
        questions=["Q1", "Q2"],
        resources=[],
        is_active=True,
    )
    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)
    return topic


@pytest.mark.asyncio
async def test_matching_even_participants(db_session):
    """Test matching with an even number of participants."""
    await create_topic(db_session)
    test_date = datetime.now(UTC) + timedelta(days=5)
    test_session = await create_session(db_session, test_date)

    users = [await create_user(db_session, 100 + i, f"u{i}") for i in range(1, 5)]
    await register_users(db_session, test_session.id, users)

    matches_count, unmatched_ids = await create_matches_for_session(
        test_session.id, db_session=db_session
    )

    assert matches_count == 2
    assert len(unmatched_ids) == 0
    await db_session.refresh(test_session)
    assert test_session.status == SessionStatus.MATCHED


@pytest.mark.asyncio
async def test_matching_odd_participants(db_session):
    """Test matching with an odd number of participants.

    With 3 users, a triple match should be created (all 3 users matched).
    """
    await create_topic(db_session)
    test_date = datetime.now(UTC) + timedelta(days=5)
    test_session = await create_session(db_session, test_date)

    users = [await create_user(db_session, 200 + i, f"u{i}_odd") for i in range(1, 4)]
    await register_users(db_session, test_session.id, users)

    matches_count, unmatched_ids = await create_matches_for_session(
        test_session.id, db_session=db_session
    )

    assert matches_count == 1
    assert len(unmatched_ids) == 0
    await db_session.refresh(test_session)
    assert test_session.status == SessionStatus.MATCHED


@pytest.mark.asyncio
async def test_matching_insufficient_participants(db_session):
    """Test matching with less than 2 participants."""
    test_date = datetime.now(UTC) + timedelta(days=5)
    test_session = await create_session(db_session, test_date)

    user = await create_user(db_session, 301, "u1_single")
    await register_users(db_session, test_session.id, [user])

    matches_count, unmatched_ids = await create_matches_for_session(
        test_session.id, db_session=db_session
    )

    assert matches_count == 0
    assert len(unmatched_ids) == 1
    assert unmatched_ids[0] == user.id


@pytest.mark.asyncio
async def test_matching_duplicate_avoidance(db_session):
    """Test that matching avoids creating duplicate pairs."""
    await create_topic(db_session)
    test_date = datetime.now(UTC) + timedelta(days=5)
    session1 = await create_session(db_session, test_date)
    session2 = await create_session(db_session, test_date + timedelta(days=7))

    users = [await create_user(db_session, 400 + i, f"u{i}_dup") for i in range(1, 5)]
    user_ids = [u.id for u in users]

    await register_users(db_session, session1.id, users)
    await create_matches_for_session(session1.id, db_session=db_session)

    result = await db_session.execute(select(Match).where(Match.session_id == session1.id))
    session1_pairs = {
        tuple(sorted((m.user1_id, m.user2_id))) for m in result.scalars().all()
    }

    await register_users(db_session, session2.id, users)
    match_repo = MatchRepository(db_session)
    past_matches = await get_previous_matches(match_repo, user_ids)

    for pair in session1_pairs:
        assert pair in past_matches

    matches2_count, _ = await create_matches_for_session(session2.id, db_session=db_session)
    assert matches2_count == 2

    result2 = await db_session.execute(select(Match).where(Match.session_id == session2.id))
    session2_pairs = {
        tuple(sorted((m.user1_id, m.user2_id))) for m in result2.scalars().all()
    }

    assert session1_pairs != session2_pairs


@pytest.mark.asyncio
async def test_get_previous_matches(db_session):
    """Test get_previous_matches function."""
    test_date = datetime.now(UTC) + timedelta(days=5)
    test_session = await create_session(db_session, test_date)
    u1 = await create_user(db_session, 601, "u1_prev")
    u2 = await create_user(db_session, 602, "u2_prev")

    match = Match(
        session_id=test_session.id,
        user1_id=u1.id,
        user2_id=u2.id,
        status=MatchStatus.CREATED,
        created_at=datetime.now(UTC),
    )
    db_session.add(match)
    await db_session.commit()

    match_repo = MatchRepository(db_session)
    past_matches = await get_previous_matches(match_repo, [u1.id, u2.id])
    expected_pair = tuple(sorted((u1.id, u2.id)))
    assert expected_pair in past_matches
