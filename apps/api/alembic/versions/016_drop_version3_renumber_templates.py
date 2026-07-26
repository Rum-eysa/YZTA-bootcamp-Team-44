"""Drop Version3 slot; renumber Version4→3, Version5→4, Version6→5

Revision ID: 016
Revises: 015
Create Date: 2026-07-26
"""

from alembic import op


revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # İki aşamalı: çakışmayı önlemek için önce geçici etiketlere taşı
    op.execute(
        """
        UPDATE job_listings SET cv_template = CASE cv_template
            WHEN 'Version3' THEN '__tmp_drop__'
            WHEN 'Version4' THEN '__tmp_v3__'
            WHEN 'Version5' THEN '__tmp_v4__'
            WHEN 'Version6' THEN '__tmp_v5__'
            ELSE cv_template
        END
        """
    )
    op.execute(
        """
        UPDATE job_listings SET cv_template = CASE cv_template
            WHEN '__tmp_drop__' THEN 'Version2'
            WHEN '__tmp_v3__' THEN 'Version3'
            WHEN '__tmp_v4__' THEN 'Version4'
            WHEN '__tmp_v5__' THEN 'Version5'
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
               'Version1', 'Version2', 'Version3', 'Version4', 'Version5'
           )
        """
    )


def downgrade() -> None:
    # Geriye dönüş yaklaşık: yeni 3/4/5 → eski 4/5/6; silinen slot geri gelmez
    op.execute(
        """
        UPDATE job_listings SET cv_template = CASE cv_template
            WHEN 'Version3' THEN 'Version4'
            WHEN 'Version4' THEN 'Version5'
            WHEN 'Version5' THEN 'Version6'
            ELSE cv_template
        END
        """
    )
