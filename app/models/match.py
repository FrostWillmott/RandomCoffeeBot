"""Match model for paired users."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Match(Base):
    """Matched pair of users for a Random Coffee session."""

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
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="created", nullable=False
    )  # created, confirmed, completed, cancelled
    meeting_time: Mapped[datetime | None] = mapped_column(DateTime)
    meeting_format: Mapped[str | None] = mapped_column(
        String(50)
    )  # zoom, meet, telegram
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="matches")
    user1: Mapped["User"] = relationship(
        foreign_keys=[user1_id], back_populates="matches_as_user1"
    )
    user2: Mapped["User"] = relationship(
        foreign_keys=[user2_id], back_populates="matches_as_user2"
    )
    topic: Mapped["Topic"] = relationship(back_populates="matches")
    feedbacks: Mapped[list["Feedback"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Match user1={self.user1_id} "
            f"user2={self.user2_id} status={self.status}>"
        )
