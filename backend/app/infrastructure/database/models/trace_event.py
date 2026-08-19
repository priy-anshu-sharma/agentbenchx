"""SQLAlchemy model for trace events."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum

from backend.app.infrastructure.database.base import Base
from backend.app.domain.traces.models import TraceEventType


class TraceEvent(Base):
    """SQLAlchemy model for trace events."""

    __tablename__ = "trace_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # Storing as string for simplicity
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<TraceEvent(id={self.id}, trace_id='{self.trace_id}', event_type='{self.event_type}', sequence_number={self.sequence_number})>"