"""SQLAlchemy model for evaluation runs."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum

from backend.app.infrastructure.database.base import Base


class RunStatus(str, Enum):
    """Possible statuses for an evaluation run."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EvaluationRun(Base):
    """SQLAlchemy model for evaluation runs."""

    __tablename__ = "evaluation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Identification fields
    task_id = Column(String(255), nullable=False, index=True)
    task_version = Column(String(50), nullable=False)
    agent_id = Column(String(255), nullable=False, index=True)
    agent_version = Column(String(50), nullable=False)
    environment_id = Column(String(255), nullable=False, index=True)
    trace_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    benchmark_id = Column(String(255), nullable=True, index=True)
    benchmark_version = Column(String(50), nullable=True)

    # Runtime fields
    status = Column(SQLEnum(RunStatus), nullable=False, default=RunStatus.PENDING, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)

    # Configuration and metadata
    configuration = Column(JSON, nullable=False, default=dict)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<EvaluationRun(id={self.id}, task_id='{self.task_id}', agent_id='{self.agent_id}', status='{self.status}')>"