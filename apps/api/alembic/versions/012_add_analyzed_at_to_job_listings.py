"""Add analyzed_at to job_listings for stale result warnings

Revision ID: 012
Revises: cfc0a82976cc
Create Date: 2026-07-19
"""

from alembic import op
import sqlalchemy as sa


revision = "012"
down_revision = "cfc0a82976cc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "job_listings",
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job_listings", "analyzed_at")
