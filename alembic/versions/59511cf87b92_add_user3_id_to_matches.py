"""add_user3_id_to_matches

Revision ID: 59511cf87b92
Revises: 5ce5de139a6b
Create Date: 2026-01-10 14:46:55.894818
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "59511cf87b92"
down_revision: str | None = "5ce5de139a6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column("matches", sa.Column("user3_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_matches_user3_id"), "matches", ["user3_id"], unique=False)
    op.create_foreign_key(
        "matches_user3_id_fkey",
        "matches",
        "users",
        ["user3_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_constraint("matches_user3_id_fkey", "matches", type_="foreignkey")
    op.drop_index(op.f("ix_matches_user3_id"), table_name="matches")
    op.drop_column("matches", "user3_id")
