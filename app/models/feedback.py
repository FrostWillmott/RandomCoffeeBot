"""Feedback model for match reviews."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User

if TYPE_CHECKING:
    from app.models.match import Match


class Feedback(Base):
    """User feedback after a Random Coffee meeting."""

    __tablename__ = "feedbacks"
    __table_args__ = (
        UniqueConstraint("match_id", "user_id", name="uq_feedback_match_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_feedback_rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    topic_difficulty: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    match: Mapped[Match] = relationship(back_populates="feedbacks")
    user: Mapped[User] = relationship(back_populates="feedbacks")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Feedback match={self.match_id} user={self.user_id} rating={self.rating}>"
