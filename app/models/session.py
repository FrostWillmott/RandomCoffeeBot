"""Session model for Random Coffee events."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SessionStatus

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.registration import Registration


class Session(Base):
    """Random Coffee session (daily event)."""

    __tablename__ = "sessions"
    __table_args__ = (UniqueConstraint("date", name="uq_session_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(
            SessionStatus,
            native_enum=False,
            length=50,
            create_constraint=False,
            values_callable=lambda e: [v.value for v in e],
        ),
        default=SessionStatus.OPEN,
        nullable=False,
        index=True,
    )
    announcement_message_id: Mapped[int | None] = mapped_column(BigInteger)
    notifications_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    registrations: Mapped[list[Registration]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    matches: Mapped[list[Match]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Session {self.date.date()} - {self.status}>"
