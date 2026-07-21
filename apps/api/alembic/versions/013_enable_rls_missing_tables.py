"""Enable Row Level Security on tables added after 002_enable_rls_policies (US-050 hotfix)

002_enable_rls_policies (revision 003) only covered the tables that existed at the
time: users, job_listings, matches, documents, agent_tasks, agent_workflows. Every
profile-detail table added since (work experience, projects, education, certificates,
exams, languages, social links, references) was left without RLS - Supabase flagged
this as "Table publicly accessible" since PostgREST exposes any public-schema table
without RLS to the anon/authenticated roles by default.

Same rationale as 003: the backend connects with the service_role key and bypasses
RLS entirely, so the app itself is unaffected. We simply enable RLS with no policies
(deny-by-default for anon/authenticated), mirroring the agent_tasks/agent_workflows
approach in 003 - defense in depth in case an anon/authenticated key is ever used
directly against Supabase's REST API.

Revision ID: 013
Revises: 012
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa

revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None

TABLES = [
    'work_experiences',
    'projects',
    'education_records',
    'certificates',
    'exams',
    'languages',
    'social_links',
    'references',
]


def upgrade() -> None:
    # Supabase auth şeması yoksa (yerel Docker Postgres) RLS atlanır
    conn = op.get_bind()
    has_auth_schema = conn.execute(
        sa.text("SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth'")
    ).scalar()
    if not has_auth_schema:
        return

    for table in TABLES:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    conn = op.get_bind()
    has_auth_schema = conn.execute(
        sa.text("SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth'")
    ).scalar()
    if not has_auth_schema:
        return

    for table in TABLES:
        op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY')
