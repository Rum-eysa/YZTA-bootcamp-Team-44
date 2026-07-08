"""Add score_breakdown column to matches table (US-021)

Revision ID: 011
Revises: 010
Create Date: 2026-07-08
"""

from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("score_breakdown", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("matches", "score_breakdown")
