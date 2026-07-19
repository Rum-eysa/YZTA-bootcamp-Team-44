"""açıklama — NO-OP (yanlış autogenerate)

Revision ID: cfc0a82976cc
Revises: 011
Create Date: 2026-07-19 11:53:53.767787

Bu revision yanlışlıkla tüm şemayı create/drop edecek şekilde
autogenerate edilmişti. Zinciri kırmamak için no-op bırakıldı;
gerçek şema 001–011 + 012 (analyzed_at) ile kurulur.
"""

# revision identifiers, used by Alembic.
revision = "cfc0a82976cc"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
