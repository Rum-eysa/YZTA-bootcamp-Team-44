"""Agent system models for future AI agent integration"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

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

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), default=AgentTaskStatus.PENDING, nullable=False
    )

    payload: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    agent_id: Mapped[str] = mapped_column(String(50), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    application_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)

    def mark_started(self) -> None:
        self.status = AgentTaskStatus.PROCESSING
        self.started_at = datetime.utcnow()

    def mark_completed(
        self,
        result: str,
        runtime_ms: float | None = None,
        token_count: int | None = None,
    ) -> None:
        self.status = AgentTaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
        self.runtime_ms = int(runtime_ms) if runtime_ms is not None else None
        self.token_count = token_count

    def mark_failed(self, error_message: str) -> None:
        self.status = AgentTaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()


class AgentWorkflow(Base):
    """Agent workflow model for multi-agent orchestration"""

    __tablename__ = "agent_workflows"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workflow_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), default=AgentTaskStatus.PENDING, nullable=False
    )

    config: Mapped[str] = mapped_column(Text, nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, default=0)

    result: Mapped[str] = mapped_column(Text, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    total_steps: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    application_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    triggered_by: Mapped[str] = mapped_column(String(36), nullable=True)

    def mark_started(self) -> None:
        self.status = AgentTaskStatus.PROCESSING
        self.started_at = datetime.utcnow()

    def mark_completed(self, result: str) -> None:
        self.status = AgentTaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        self.status = AgentTaskStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
