"""Agent system models for future AI agent integration"""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models import Base


class AgentTaskStatus(str, Enum):
    """Agent task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTask(Base):
    """Agent task model for tracking AI agent operations"""
    __tablename__ = "agent_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=AgentTaskStatus.PENDING, nullable=False)
    
    # Task payload and results
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Metadata
    agent_id: Mapped[str] = mapped_column(String(50), nullable=True)
    priority: Mapped[int] = mapped_column(default=5)  # 1-10, higher is more important
    retry_count: Mapped[int] = mapped_column(default=0)
    max_retries: Mapped[int] = mapped_column(default=3)
    
    # Timestamps
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Related entities
    application_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)


class AgentWorkflow(Base):
    """Agent workflow model for multi-agent orchestration"""
    __tablename__ = "agent_workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=AgentTaskStatus.PENDING, nullable=False)
    
    # Workflow configuration
    config: Mapped[str] = mapped_column(Text, nullable=False)  # JSON config
    current_step: Mapped[int] = mapped_column(default=0)
    total_steps: Mapped[int] = mapped_column(default=1)
    
    # Results
    result: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Related entities
    application_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    triggered_by: Mapped[str] = mapped_column(String(36), nullable=True)  # User ID
