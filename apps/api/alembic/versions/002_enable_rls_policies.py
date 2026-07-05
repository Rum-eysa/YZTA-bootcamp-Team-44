"""Enable Row Level Security + policies on Supabase tables (US-002)

Backend connects to Supabase Postgres with the service_role connection
string, which bypasses RLS entirely - so the app itself is unaffected.
This migration protects the data in case the anon/authenticated keys
(SUPABASE_ANON_KEY) are ever used directly against Supabase's REST API:
without RLS enabled, a leaked anon key can read/write every row directly.

We enable RLS on every table and add explicit policies scoped to
Supabase's own `authenticated` role using auth.uid(). Our custom
FastAPI JWT is a separate token from Supabase Auth, so `authenticated`
requests via anon key still can't match auth.uid() to our rows - the
net effect is anon/authenticated are denied by default (defense in
depth), while service_role (used by the backend) is unaffected.

Revision ID: 002
Revises: 001
Create Date: 2026-07-06

"""
from alembic import op

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

TABLES = ['users', 'job_listings', 'matches', 'documents', 'agent_tasks', 'agent_workflows']


def upgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')

    # users: yalnızca kendi satırını görebilir/güncelleyebilir (Supabase auth.uid() ile)
    op.execute(
        "CREATE POLICY users_self_select ON users FOR SELECT "
        "USING (auth.uid()::text = id)"
    )
    op.execute(
        "CREATE POLICY users_self_update ON users FOR UPDATE "
        "USING (auth.uid()::text = id)"
    )

    # job_listings: kullanıcı sadece kendi oluşturduğu ilanları görebilir
    op.execute(
        "CREATE POLICY job_listings_owner_select ON job_listings FOR SELECT "
        "USING (auth.uid()::text = created_by)"
    )

    # matches / documents: kullanıcı sadece kendi kayıtlarını görebilir
    op.execute(
        "CREATE POLICY matches_owner_select ON matches FOR SELECT "
        "USING (auth.uid()::text = user_id)"
    )
    op.execute(
        "CREATE POLICY documents_owner_select ON documents FOR SELECT "
        "USING (auth.uid()::text = user_id)"
    )

    # agent_tasks / agent_workflows: policy yok - RLS açık olduğundan
    # anon/authenticated rolleri için varsayılan tam ret geçerli olur


def downgrade() -> None:
    op.execute('DROP POLICY IF EXISTS documents_owner_select ON documents')
    op.execute('DROP POLICY IF EXISTS matches_owner_select ON matches')
    op.execute('DROP POLICY IF EXISTS job_listings_owner_select ON job_listings')
    op.execute('DROP POLICY IF EXISTS users_self_update ON users')
    op.execute('DROP POLICY IF EXISTS users_self_select ON users')

    for table in TABLES:
        op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY')
