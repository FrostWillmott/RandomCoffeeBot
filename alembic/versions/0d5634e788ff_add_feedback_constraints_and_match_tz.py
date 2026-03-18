"""Add feedback constraints and match timezone columns.

Revision ID: 0d5634e788ff
Revises: 59511cf87b92
Create Date: 2026-02-03 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

revision: str = "0d5634e788ff"
down_revision: str | None = "59511cf87b92"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add feedback unique/check constraints and timezone to match columns."""
    op.create_unique_constraint(
        "uq_feedback_match_user", "feedbacks", ["match_id", "user_id"]
    )
    op.create_check_constraint(
        "ck_feedback_rating_range",
        "feedbacks",
        "rating >= 1 AND rating <= 5",
    )
    op.alter_column(
        "matches",
        "meeting_time",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "matches",
        "confirmed_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Revert feedback constraints and match timezone columns."""
    op.alter_column(
        "matches",
        "confirmed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "matches",
        "meeting_time",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    op.drop_constraint("ck_feedback_rating_range", "feedbacks", type_="check")
    op.drop_constraint("uq_feedback_match_user", "feedbacks", type_="unique")
