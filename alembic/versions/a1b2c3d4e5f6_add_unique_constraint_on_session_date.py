"""Add unique constraint on session date.

Revision ID: a1b2c3d4e5f6
Revises: 0d5634e788ff
Create Date: 2026-07-03 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "0d5634e788ff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique constraint on session date."""
    op.create_unique_constraint("uq_session_date", "sessions", ["date"])


def downgrade() -> None:
    """Remove unique constraint on session date."""
    op.drop_constraint("uq_session_date", "sessions", type_="unique")
