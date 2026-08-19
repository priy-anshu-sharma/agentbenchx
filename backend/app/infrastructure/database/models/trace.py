"""SQLAlchemy model for traces."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum

from backend.app.infrastructure.database.base import Base


class Trace(Base):
    """SQLAlchemy model for traces."""

    __tablename__ = "traces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(String(255), nullable=False, index=True)
    task_id = Column(String(255), nullable=False, index=True)
    environment_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    run_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_runs.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<Trace(id={self.id}, run_id='{self.run_id}', agent_id='{self.agent_id}', task_id='{self.task_id}', status='{self.status}')>"