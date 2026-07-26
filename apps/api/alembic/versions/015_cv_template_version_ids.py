"""Migrate cv_template values to VersionN ids

Revision ID: 015
Revises: 014
Create Date: 2026-07-26
"""

from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "job_listings",
        "cv_template",
        existing_type=sa.String(length=10),
        type_=sa.String(length=20),
        existing_nullable=False,
        server_default="Version1",
    )
    op.execute(
        """
        UPDATE job_listings SET cv_template = CASE cv_template
            WHEN '1' THEN 'Version1'
            WHEN '2' THEN 'Version2'
            WHEN '3' THEN 'Version3'
            WHEN '4' THEN 'Version4'
            WHEN '5' THEN 'Version5'
            WHEN '6' THEN 'Version6'
            ELSE cv_template
        END
        """
    )
    op.execute(
        """
        UPDATE job_listings
        SET cv_template = 'Version1'
        WHERE cv_template IS NULL
           OR cv_template NOT IN (
               'Version1', 'Version2', 'Version3',
               'Version4', 'Version5', 'Version6'
           )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE job_listings SET cv_template = CASE cv_template
            WHEN 'Version1' THEN '1'
            WHEN 'Version2' THEN '2'
            WHEN 'Version3' THEN '3'
            WHEN 'Version4' THEN '4'
            WHEN 'Version5' THEN '5'
            WHEN 'Version6' THEN '6'
            ELSE '1'
        END
        """
    )
    op.alter_column(
        "job_listings",
        "cv_template",
        existing_type=sa.String(length=20),
        type_=sa.String(length=10),
        existing_nullable=False,
        server_default="1",
    )
