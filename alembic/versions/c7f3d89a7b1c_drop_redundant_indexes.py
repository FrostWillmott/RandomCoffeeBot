"""Drop redundant indexes that duplicate unique constraints.

Revision ID: c7f3d89a7b1c
Revises: 99bfa2094c82
Create Date: 2025-12-31 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "c7f3d89a7b1c"
down_revision: str | None = "99bfa2094c82"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove redundant indexes created earlier."""
    op.execute("DROP INDEX IF EXISTS ix_registrations_session_user")
    op.execute("DROP INDEX IF EXISTS ix_matches_user1")
    op.execute("DROP INDEX IF EXISTS ix_matches_user2")


def downgrade() -> None:
    """Re-create the redundant indexes when rolling back."""
    op.create_index(
        "ix_registrations_session_user",
        "registrations",
        ["session_id", "user_id"],
        unique=False,
    )
    op.create_index("ix_matches_user1", "matches", ["user1_id"], unique=False)
    op.create_index("ix_matches_user2", "matches", ["user2_id"], unique=False)
