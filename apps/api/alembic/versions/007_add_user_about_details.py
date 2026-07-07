"""Add about-details columns to users

Revision ID: 007
Revises: 006
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("gender", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("nationality", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("driver_license", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("military_status", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "military_status")
    op.drop_column("users", "driver_license")
    op.drop_column("users", "nationality")
    op.drop_column("users", "gender")

