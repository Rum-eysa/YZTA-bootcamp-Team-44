"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table (profil alanları dahil - ajanların hafıza katmanı için)
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('target_position', sa.String(255), nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('experience_years', sa.Float(), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('experience_summary', sa.Text(), nullable=True),
        sa.Column('tone_preference', sa.String(50), nullable=True, server_default='professional'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create job_listings table (Analiz Ajanı çıktısı)
    op.create_table(
        'job_listings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('required_skills', sa.Text(), nullable=True),
        sa.Column('nice_to_have_skills', sa.Text(), nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('parsed_json', sa.Text(), nullable=True),
        sa.Column('analysis_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_job_listings_created_by', 'job_listings', ['created_by'])

    # Create matches table (Eşleştirme Ajanı çıktısı)
    op.create_table(
        'matches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('listing_id', sa.String(36), sa.ForeignKey('job_listings.id'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('matched_skills', sa.Text(), nullable=True),
        sa.Column('missing_skills', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_matches_user_id', 'matches', ['user_id'])
    op.create_index('ix_matches_listing_id', 'matches', ['listing_id'])

    # Create documents table (CV / önyazı Üretim Ajanı çıktısı)
    op.create_table(
        'documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('listing_id', sa.String(36), sa.ForeignKey('job_listings.id'), nullable=True),
        sa.Column('doc_type', sa.String(20), nullable=False),
        sa.Column('cv_url', sa.String(1000), nullable=True),
        sa.Column('cover_letter_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])
    op.create_index('ix_documents_listing_id', 'documents', ['listing_id'])

    # Create agent_tasks table (agent orkestrasyonu takibi)
    op.create_table(
        'agent_tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('agent_id', sa.String(50), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_id', sa.String(36), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
    )
    op.create_index('ix_agent_tasks_task_type', 'agent_tasks', ['task_type'])
    op.create_index('ix_agent_tasks_application_id', 'agent_tasks', ['application_id'])
    op.create_index('ix_agent_tasks_user_id', 'agent_tasks', ['user_id'])

    # Create agent_workflows table (multi-agent orkestrasyon)
    op.create_table(
        'agent_workflows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('config', sa.Text(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_steps', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_id', sa.String(36), nullable=True),
        sa.Column('triggered_by', sa.String(36), nullable=True),
    )
    op.create_index('ix_agent_workflows_workflow_type', 'agent_workflows', ['workflow_type'])
    op.create_index('ix_agent_workflows_application_id', 'agent_workflows', ['application_id'])


def downgrade() -> None:
    op.drop_index('ix_agent_workflows_application_id', 'agent_workflows')
    op.drop_index('ix_agent_workflows_workflow_type', 'agent_workflows')
    op.drop_table('agent_workflows')

    op.drop_index('ix_agent_tasks_user_id', 'agent_tasks')
    op.drop_index('ix_agent_tasks_application_id', 'agent_tasks')
    op.drop_index('ix_agent_tasks_task_type', 'agent_tasks')
    op.drop_table('agent_tasks')

    op.drop_index('ix_documents_listing_id', 'documents')
    op.drop_index('ix_documents_user_id', 'documents')
    op.drop_table('documents')

    op.drop_index('ix_matches_listing_id', 'matches')
    op.drop_index('ix_matches_user_id', 'matches')
    op.drop_table('matches')

    op.drop_index('ix_job_listings_created_by', 'job_listings')
    op.drop_table('job_listings')

    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
