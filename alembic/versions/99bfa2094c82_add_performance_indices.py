"""Add performance indices.

Revision ID: 99bfa2094c82
Revises: 8b9ad2733ab5
Create Date: 2025-12-29 19:23:25.239154
"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "99bfa2094c82"
down_revision: str | None = "8b9ad2733ab5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add performance indices for frequently queried columns."""
    # Matches: composite index for session + status queries
    op.create_index(
        "ix_matches_session_status", "matches", ["session_id", "status"], unique=False
    )

    # Sessions: index for status + date queries
    op.create_index("ix_sessions_status_date", "sessions", ["status", "date"], unique=False)

    # Topics: index for is_active + difficulty
    op.create_index(
        "ix_topics_active_difficulty", "topics", ["is_active", "difficulty"], unique=False
    )


def downgrade() -> None:
    """Remove performance indices."""
    op.drop_index("ix_topics_active_difficulty", table_name="topics")
    op.drop_index("ix_sessions_status_date", table_name="sessions")
    op.drop_index("ix_matches_session_status", table_name="matches")
