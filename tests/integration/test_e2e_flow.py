"""End-to-end integration tests for complete user flows."""

import pytest
from sqlalchemy import select

from app.models.enums import MatchStatus, SessionStatus
from app.models.match import Match
from app.models.registration import Registration
from app.services.matching import create_matches_for_session


@pytest.mark.asyncio
async def test_complete_registration_to_matching_flow(
    db_session, user_factory, session_factory, topic_factory
):
    """Test complete flow: create session → register users → create matches.

    Scenario:
        1. Create a session
        2. Register 4 users
        3. Close session and create matches
        4. Verify 2 matches are created
        5. Verify session status updated to MATCHED
    """
    await topic_factory(title="Topic 1")
    await topic_factory(title="Topic 2")

    session = await session_factory(status=SessionStatus.OPEN)
    assert session.status == SessionStatus.OPEN

    users = []
    for i in range(4):
        user = await user_factory(username=f"user_{i}")
        users.append(user)

        reg = Registration(user_id=user.id, session_id=session.id)
        db_session.add(reg)

    await db_session.commit()

    result = await db_session.execute(
        select(Registration).where(Registration.session_id == session.id)
    )
    registrations = result.scalars().all()
    assert len(registrations) == 4

    matches_count, unmatched_ids = await create_matches_for_session(
        session.id, db_session=db_session
    )

    assert matches_count == 2
    assert len(unmatched_ids) == 0

    await db_session.refresh(session)
    assert session.status == SessionStatus.MATCHED

    result = await db_session.execute(select(Match).where(Match.session_id == session.id))
    matches = result.scalars().all()
    assert len(matches) == 2

    matched_user_ids = set()
    for match in matches:
        assert match.status == MatchStatus.CREATED
        assert match.topic_id is not None
        matched_user_ids.add(match.user1_id)
        matched_user_ids.add(match.user2_id)

    assert len(matched_user_ids) == 4
    for user in users:
        assert user.id in matched_user_ids


@pytest.mark.asyncio
async def test_multi_session_no_duplicate_pairs(
    db_session, user_factory, session_factory, topic_factory
):
    """Test that multiple sessions avoid creating duplicate pairs.

    Scenario:
        1. Create 4 users
        2. Session 1: Match all users (creates 2 pairs)
        3. Session 2: Match the same users (should create different pairs)
        4. Verify no duplicate pairs across sessions
    """
    await topic_factory(title="Topic 1")
    await topic_factory(title="Topic 2")

    users = [await user_factory() for _ in range(4)]

    session1 = await session_factory(days_ahead=5)
    for user in users:
        db_session.add(Registration(user_id=user.id, session_id=session1.id))
    await db_session.commit()

    matches1_count, _ = await create_matches_for_session(session1.id, db_session=db_session)
    assert matches1_count == 2

    result = await db_session.execute(select(Match).where(Match.session_id == session1.id))
    session1_matches = result.scalars().all()
    session1_pairs = {tuple(sorted((m.user1_id, m.user2_id))) for m in session1_matches}

    session2 = await session_factory(days_ahead=12)
    for user in users:
        db_session.add(Registration(user_id=user.id, session_id=session2.id))
    await db_session.commit()

    matches2_count, _ = await create_matches_for_session(session2.id, db_session=db_session)
    assert matches2_count == 2

    await db_session.flush()
    result = await db_session.execute(select(Match).where(Match.session_id == session2.id))
    session2_matches = result.scalars().all()
    session2_pairs = {tuple(sorted((m.user1_id, m.user2_id))) for m in session2_matches}

    if len(session1_pairs) < 3:
        assert session1_pairs != session2_pairs


@pytest.mark.asyncio
async def test_odd_number_users_one_unmatched(
    db_session, user_factory, session_factory, topic_factory
):
    """Test that an odd number of users results in proper matching.

    Scenario:
        1. Create a session
        2. Register 5 users
        3. Create matches
        4. Verify 2 matches created (1 triple + 1 pair), 0 users unmatched
    """
    await topic_factory()

    session = await session_factory()
    users = [await user_factory() for _ in range(5)]

    for user in users:
        db_session.add(Registration(user_id=user.id, session_id=session.id))
    await db_session.commit()

    matches_count, unmatched_ids = await create_matches_for_session(
        session.id, db_session=db_session
    )

    assert matches_count == 2
    assert len(unmatched_ids) == 0


@pytest.mark.asyncio
async def test_session_lifecycle_states(db_session, session_factory):
    """Test session transitions through lifecycle states.

    Scenario:
        1. Session created as OPEN
        2. After matching, becomes MATCHED
        3. Can be marked as COMPLETED
    """
    session = await session_factory(status=SessionStatus.OPEN)
    assert session.status == SessionStatus.OPEN

    session.status = SessionStatus.CLOSED
    await db_session.commit()
    await db_session.refresh(session)
    assert session.status == SessionStatus.CLOSED

    session.status = SessionStatus.MATCHED
    await db_session.commit()
    await db_session.refresh(session)
    assert session.status == SessionStatus.MATCHED

    session.status = SessionStatus.COMPLETED
    await db_session.commit()
    await db_session.refresh(session)
    assert session.status == SessionStatus.COMPLETED


@pytest.mark.asyncio
async def test_registration_constraints(db_session, user_factory, session_factory):
    """Test that a user cannot register twice for the same session.

    Scenario:
        1. User registers for session
        2. Attempt to register the same user again
        3. Verify database constraint prevents duplicate
    """
    from sqlalchemy.exc import IntegrityError

    user = await user_factory()
    session = await session_factory()

    reg1 = Registration(user_id=user.id, session_id=session.id)
    db_session.add(reg1)
    await db_session.commit()

    reg2 = Registration(user_id=user.id, session_id=session.id)
    db_session.add(reg2)

    with pytest.raises(IntegrityError):
        await db_session.commit()
