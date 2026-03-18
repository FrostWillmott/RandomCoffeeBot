"""Enumerations for database models."""

from enum import StrEnum


class SessionStatus(StrEnum):
    """Status of a Random Coffee session."""

    OPEN = "open"
    CLOSED = "closed"
    MATCHING = "matching"
    MATCHED = "matched"
    COMPLETED = "completed"


class MatchStatus(StrEnum):
    """Status of a match between two users."""

    CREATED = "created"
    NOTIFIED = "notified"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
