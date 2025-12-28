"""Registration model for session participation."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="registrations")
    user: Mapped["User"] = relationship(back_populates="registrations")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Registration user={self.user_id} session={self.session_id}>"
