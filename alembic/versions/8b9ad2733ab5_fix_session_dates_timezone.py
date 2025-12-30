"""Fix session dates timezone.

Revision ID: 8b9ad2733ab5
Revises: efed37957c63
Create Date: 2025-12-29 15:18:50.237749
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "8b9ad2733ab5"
down_revision: str | None = "efed37957c63"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Fix timezone for datetime columns."""
    # Convert datetime columns to timezone-aware
    op.alter_column(
        "sessions",
        "date",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "sessions",
        "registration_deadline",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "sessions",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "topics",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "matches",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "registrations",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )
    op.alter_column(
        "feedbacks",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
    )


def downgrade() -> None:
    """Revert timezone for datetime columns."""
    # Convert datetime columns back to timezone-naive
    op.alter_column(
        "sessions",
        "date",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "sessions",
        "registration_deadline",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "sessions",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "topics",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "matches",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "registrations",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "feedbacks",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
