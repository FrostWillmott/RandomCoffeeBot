"""Registration model for session participation."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.session import Session
from app.models.user import User


class Registration(Base):
    """User registration for a Random Coffee session."""

    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    session: Mapped[Session] = relationship(back_populates="registrations")
    user: Mapped[User] = relationship(back_populates="registrations")

    __table_args__ = (UniqueConstraint("session_id", "user_id", name="uq_session_user"),)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Registration user={self.user_id} session={self.session_id}>"
