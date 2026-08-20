"""Trace query domain models for filtering and pagination."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from backend.app.domain.traces.models import TraceEventType


class TraceQuery(BaseModel):
    """Domain model for querying traces with filtering and pagination options."""

    run_id: Optional[UUID] = Field(None, description="Filter by execution run ID")
    task_id: Optional[str] = Field(None, description="Filter by task ID")
    agent_id: Optional[str] = Field(None, description="Filter by agent ID")
    event_type: Optional[TraceEventType] = Field(None, description="Filter by trace event type")
    created_after: Optional[datetime] = Field(None, description="Filter traces created after this timestamp")
    created_before: Optional[datetime] = Field(None, description="Filter traces created before this timestamp")
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of results to return")
    offset: Optional[int] = Field(None, ge=0, description="Number of results to skip for pagination")

    @field_validator('created_before')
    @classmethod
    def validate_time_range(cls, v, info):
        """Validate that created_after is before created_before when both are provided."""
        if v is not None and 'created_after' in info.data and info.data['created_after'] is not None:
            if info.data['created_after'] > v:
                raise ValueError('created_after must be before created_before')
        return v

    model_config = {
        "json_encoders": {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
    }