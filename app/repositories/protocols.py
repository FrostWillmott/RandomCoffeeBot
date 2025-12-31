"""Protocol interfaces for repositories."""

from datetime import datetime
from typing import Protocol

from app.models.enums import SessionStatus
from app.models.feedback import Feedback
from app.models.match import Match
from app.models.registration import Registration
from app.models.session import Session
from app.models.topic import Topic
from app.models.user import User


class UserRepositoryProtocol(Protocol):
    """Protocol for User repository."""

    async def get_by_id(self, id: int) -> User | None:
        """Get user by ID."""
        ...

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        ...

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        level: str = "middle",
    ) -> User:
        """Get existing user or create new one."""
        ...

    async def create(self, entity: User) -> User:
        """Create new user."""
        ...

    async def update(self, entity: User) -> User:
        """Update existing user."""
        ...

    async def mark_inactive(self, user_id: int) -> bool:
        """Mark user as inactive."""
        ...

    async def get_active_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get active user by Telegram ID."""
        ...


class SessionRepositoryProtocol(Protocol):
    """Protocol for Session repository."""

    async def get_by_id(self, id: int) -> Session | None:
        """Get session by ID."""
        ...

    async def get_by_date(self, date: datetime) -> Session | None:
        """Get session by date."""
        ...

    async def get_next_open_session(self, current_time: datetime) -> Session | None:
        """Get next open session with future registration deadline."""
        ...

    async def get_sessions_by_status(self, status: SessionStatus) -> list[Session]:
        """Get all sessions with specific status."""
        ...

    async def get_expired_open_sessions(self, current_time: datetime) -> list[Session]:
        """Get open sessions past their registration deadline."""
        ...

    async def get_closed_sessions_ready_for_matching(
        self, current_time: datetime
    ) -> list[Session]:
        """Get closed sessions ready for matching."""
        ...

    async def get_open_session_by_announcement(self, message_id: int) -> Session | None:
        """Get open session by announcement message ID."""
        ...

    async def create(self, entity: Session) -> Session:
        """Create new session."""
        ...

    async def update(self, entity: Session) -> Session:
        """Update existing session."""
        ...


class MatchRepositoryProtocol(Protocol):
    """Protocol for Match repository."""

    async def get_by_id(self, id: int) -> Match | None:
        """Get match by ID."""
        ...

    async def get_by_session_id(self, session_id: int) -> list[Match]:
        """Get all matches for a session."""
        ...

    async def get_by_session_id_with_relations(self, session_id: int) -> list[Match]:
        """Get all matches for a session with user and topic relations loaded."""
        ...

    async def get_previous_matches_for_users(
        self, user_ids: list[int]
    ) -> set[tuple[int, int]]:
        """Get all previous match pairs for given users."""
        ...

    async def get_topic_ids_used_by_users(self, user1_id: int, user2_id: int) -> set[int]:
        """Get all topic IDs used in matches involving these users."""
        ...

    async def create(self, entity: Match) -> Match:
        """Create new match."""
        ...

    async def update(self, entity: Match) -> Match:
        """Update existing match."""
        ...


class RegistrationRepositoryProtocol(Protocol):
    """Protocol for Registration repository."""

    async def get_by_id(self, id: int) -> Registration | None:
        """Get registration by ID."""
        ...

    async def get_by_session_and_user(
        self, session_id: int, user_id: int
    ) -> Registration | None:
        """Get registration by session and user."""
        ...

    async def get_by_session_id(self, session_id: int) -> list[Registration]:
        """Get all registrations for a session."""
        ...

    async def get_by_session_id_with_users(self, session_id: int) -> list[Registration]:
        """Get all registrations for a session with user relations loaded."""
        ...

    async def exists(self, session_id: int, user_id: int) -> bool:
        """Check if registration exists."""
        ...

    async def create(self, entity: Registration) -> Registration:
        """Create new registration."""
        ...

    async def delete(self, entity: Registration) -> None:
        """Delete registration."""
        ...


class FeedbackRepositoryProtocol(Protocol):
    """Protocol for Feedback repository."""

    async def get_by_id(self, id: int) -> Feedback | None:
        """Get feedback by ID."""
        ...

    async def get_by_match_id(self, match_id: int) -> list[Feedback]:
        """Get all feedback for a match."""
        ...

    async def get_by_user_id(self, user_id: int) -> list[Feedback]:
        """Get all feedback from a user."""
        ...

    async def get_by_match_and_user(self, match_id: int, user_id: int) -> Feedback | None:
        """Get feedback by match and user."""
        ...

    async def exists(self, match_id: int, user_id: int) -> bool:
        """Check if feedback exists for match and user."""
        ...

    async def create(self, entity: Feedback) -> Feedback:
        """Create new feedback."""
        ...


class TopicRepositoryProtocol(Protocol):
    """Protocol for Topic repository."""

    async def get_by_id(self, id: int) -> Topic | None:
        """Get topic by ID."""
        ...

    async def get_active_by_difficulty(self, difficulty: str) -> list[Topic]:
        """Get all active topics by difficulty level."""
        ...

    async def get_active(self) -> list[Topic]:
        """Get all active topics."""
        ...

    async def get_least_used_active_topics(
        self, difficulty: str, limit: int = 10
    ) -> list[Topic]:
        """Get least used active topics by difficulty."""
        ...

    async def increment_usage(self, topic_id: int) -> Topic | None:
        """Increment usage count for a topic."""
        ...

    async def create(self, entity: Topic) -> Topic:
        """Create new topic."""
        ...

    async def update(self, entity: Topic) -> Topic:
        """Update existing topic."""
        ...
