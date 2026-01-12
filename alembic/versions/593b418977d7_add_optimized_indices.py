"""Add optimized indices for frequently queried columns.

Revision ID: 593b418977d7
Revises: ca2690e7165d
Create Date: 2026-01-12 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "593b418977d7"
down_revision: str | None = "ca2690e7165d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add optimized indices for frequently queried columns."""
    op.create_index(op.f("ix_sessions_status"), "sessions", ["status"], unique=False)
    op.create_index(
        "ix_topics_active_difficulty", "topics", ["is_active", "difficulty"], unique=False
    )


def downgrade() -> None:
    """Remove optimized indices."""
    op.drop_index("ix_topics_active_difficulty", table_name="topics")
    op.drop_index(op.f("ix_sessions_status"), table_name="sessions")
