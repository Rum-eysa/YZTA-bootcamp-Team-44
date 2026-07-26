"""Add cv_template to job_listings

Revision ID: 014
Revises: 013
Create Date: 2026-07-26
"""

from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "job_listings",
        sa.Column(
            "cv_template",
            sa.String(length=10),
            nullable=False,
            server_default="1",
        ),
    )


def downgrade() -> None:
    op.drop_column("job_listings", "cv_template")
