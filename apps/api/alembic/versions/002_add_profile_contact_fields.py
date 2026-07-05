"""Add phone, location, birth_year to users

Revision ID: 002
Revises: 001
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("location", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("birth_year", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "birth_year")
    op.drop_column("users", "location")
    op.drop_column("users", "phone")
