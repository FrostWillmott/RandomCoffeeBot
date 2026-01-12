"""Match model for paired users."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MatchStatus
from app.models.feedback import Feedback
from app.models.session import Session
from app.models.topic import Topic
from app.models.user import User


class Match(Base):
    """Matched a pair of users for a Random Coffee session."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user1_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user2_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user3_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default=MatchStatus.CREATED, nullable=False, index=True
    )
    meeting_time: Mapped[datetime | None] = mapped_column(DateTime)
    meeting_format: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)

    session: Mapped[Session] = relationship(back_populates="matches")
    user1: Mapped[User] = relationship(
        foreign_keys=[user1_id], back_populates="matches_as_user1"
    )
    user2: Mapped[User] = relationship(
        foreign_keys=[user2_id], back_populates="matches_as_user2"
    )
    user3: Mapped[User | None] = relationship(
        foreign_keys=[user3_id], back_populates="matches_as_user3"
    )
    topic: Mapped[Topic | None] = relationship(back_populates="matches")
    feedbacks: Mapped[list[Feedback]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        if self.user3_id:
            return (
                f"<Match user1={self.user1_id} user2={self.user2_id} "
                f"user3={self.user3_id} status={self.status}>"
            )
        return f"<Match user1={self.user1_id} user2={self.user2_id} status={self.status}>"
