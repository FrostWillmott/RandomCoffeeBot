"""Remove user level column.

Revision ID: 5ce5de139a6b
Revises: 593b418977d7
Create Date: 2026-01-03 14:47:00.375757
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "5ce5de139a6b"
down_revision: str | None = "593b418977d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove level column from users table."""
    op.drop_column("users", "level")


def downgrade() -> None:
    """Re-add level column to users table."""
    op.add_column(
        "users",
        sa.Column("level", sa.String(length=20), nullable=False, server_default="middle"),
    )
