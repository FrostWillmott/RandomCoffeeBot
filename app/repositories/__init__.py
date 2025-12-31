"""Repository layer for data access."""

from app.repositories.base import BaseRepository
from app.repositories.feedback import FeedbackRepository
from app.repositories.match import MatchRepository
from app.repositories.protocols import (
    FeedbackRepositoryProtocol,
    MatchRepositoryProtocol,
    RegistrationRepositoryProtocol,
    SessionRepositoryProtocol,
    TopicRepositoryProtocol,
    UserRepositoryProtocol,
)
from app.repositories.registration import RegistrationRepository
from app.repositories.session import SessionRepository
from app.repositories.topic import TopicRepository
from app.repositories.user import UserRepository

__all__ = [
    "BaseRepository",
    "FeedbackRepository",
    "FeedbackRepositoryProtocol",
    "MatchRepository",
    "MatchRepositoryProtocol",
    "RegistrationRepository",
    "RegistrationRepositoryProtocol",
    "SessionRepository",
    "SessionRepositoryProtocol",
    "TopicRepository",
    "TopicRepositoryProtocol",
    "UserRepository",
    "UserRepositoryProtocol",
]
