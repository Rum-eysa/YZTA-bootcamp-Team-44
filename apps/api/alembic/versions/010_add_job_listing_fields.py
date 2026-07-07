"""Add editable detail fields + application stage to job_listings (US-053†)

Revision ID: 010
Revises: 009
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("job_listings", sa.Column("location", sa.String(length=255), nullable=True))
    op.add_column(
        "job_listings", sa.Column("employment_type", sa.String(length=100), nullable=True)
    )
    op.add_column("job_listings", sa.Column("company_about", sa.Text(), nullable=True))
    op.add_column("job_listings", sa.Column("extra_notes", sa.Text(), nullable=True))
    op.add_column("job_listings", sa.Column("benefits", sa.Text(), nullable=True))
    op.add_column(
        "job_listings", sa.Column("experience_level", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "job_listings", sa.Column("education_level", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "job_listings", sa.Column("military_status", sa.String(length=50), nullable=True)
    )
    op.add_column("job_listings", sa.Column("languages", sa.Text(), nullable=True))
    op.add_column(
        "job_listings", sa.Column("driver_license", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "job_listings",
        sa.Column(
            "application_stage",
            sa.String(length=30),
            nullable=False,
            server_default="review",
        ),
    )


def downgrade() -> None:
    op.drop_column("job_listings", "application_stage")
    op.drop_column("job_listings", "driver_license")
    op.drop_column("job_listings", "languages")
    op.drop_column("job_listings", "military_status")
    op.drop_column("job_listings", "education_level")
    op.drop_column("job_listings", "experience_level")
    op.drop_column("job_listings", "benefits")
    op.drop_column("job_listings", "extra_notes")
    op.drop_column("job_listings", "company_about")
    op.drop_column("job_listings", "employment_type")
    op.drop_column("job_listings", "location")
