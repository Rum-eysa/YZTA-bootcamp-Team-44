"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-06-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('university', sa.String(255), nullable=False),
        sa.Column('department', sa.String(255), nullable=False),
        sa.Column('grade', sa.String(10), nullable=False),
        sa.Column('gpa', sa.Float(), nullable=False),
        sa.Column('skills', sa.Text(), nullable=False),
        sa.Column('experience', sa.Text(), nullable=False),
        sa.Column('motivation', sa.Text(), nullable=False),
        sa.Column('github_url', sa.String(500), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('ai_score', sa.Float(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    
    # Create agent_tasks table (for future agent system integration)
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
    
    # Create agent_workflows table (for future multi-agent orchestration)
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
    
    op.drop_index('ix_applications_user_id', 'applications')
    op.drop_table('applications')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
