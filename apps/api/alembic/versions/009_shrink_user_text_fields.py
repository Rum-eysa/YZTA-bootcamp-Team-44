"""Shrink user text fields (full_name, target_position, location) to 50 chars

Revision ID: 009
Revises: 008
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Mevcut uzun kayıtları 50 karaktere kırp (tip küçültmeden önce hata olmasın)
    op.execute("UPDATE users SET full_name = LEFT(full_name, 50) WHERE full_name IS NOT NULL")
    op.execute(
        "UPDATE users SET target_position = LEFT(target_position, 50) "
        "WHERE target_position IS NOT NULL"
    )
    op.execute("UPDATE users SET location = LEFT(location, 50) WHERE location IS NOT NULL")

    op.alter_column(
        "users",
        "full_name",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "target_position",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "location",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "location",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "target_position",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "full_name",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
