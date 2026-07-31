"""Add document_language to job_listings

Revision ID: 018
Revises: 017
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa


revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "job_listings",
        sa.Column(
            "document_language",
            sa.String(length=8),
            nullable=False,
            server_default="tr",
        ),
    )


def downgrade() -> None:
    op.drop_column("job_listings", "document_language")
