"""Add unique constraint and timezone for all datetime columns.

Revision ID: ca2690e7165d
Revises: 10f6fb89b5be
Create Date: 2026-01-12 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "ca2690e7165d"
down_revision: str | None = "10f6fb89b5be"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique constraint and convert all datetime columns to timezone-aware."""
    op.create_unique_constraint(
        "uq_session_user", "registrations", ["session_id", "user_id"]
    )

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
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "topics",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "matches",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "registrations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "feedbacks",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Revert unique constraint and timezone changes."""
    op.alter_column(
        "feedbacks",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "registrations",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "matches",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "topics",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "sessions",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "sessions",
        "registration_deadline",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "sessions",
        "date",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
    )
    op.drop_constraint("uq_session_user", "registrations", type_="unique")
