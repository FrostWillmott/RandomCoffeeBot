"""User model."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """Telegram user participating in Random Coffee."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    registrations: Mapped[list[Registration]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    matches_as_user1: Mapped[list[Match]] = relationship(
        foreign_keys="Match.user1_id",
        back_populates="user1",
        cascade="all, delete-orphan",
    )
    matches_as_user2: Mapped[list[Match]] = relationship(
        foreign_keys="Match.user2_id",
        back_populates="user2",
        cascade="all, delete-orphan",
    )
    matches_as_user3: Mapped[list[Match]] = relationship(
        foreign_keys="Match.user3_id",
        back_populates="user3",
        cascade="all, delete-orphan",
    )
    feedbacks: Mapped[list[Feedback]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User {self.username or self.telegram_id}>"
