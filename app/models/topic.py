"""Topic model for discussion themes."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Topic(Base):
    """Discussion topic for Random Coffee meetings."""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # python_core, async, databases, etc.
    difficulty: Mapped[str] = mapped_column(
        String(20), default="middle", nullable=False
    )
    questions: Mapped[list[str]] = mapped_column(
        ARRAY(Text), default=list, nullable=False
    )
    resources: Mapped[list[str]] = mapped_column(
        ARRAY(String(500)), default=list, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    matches: Mapped[list["Match"]] = relationship(back_populates="topic")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Topic {self.title} ({self.category})>"
