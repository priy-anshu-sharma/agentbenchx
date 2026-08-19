"""Task domain models for AgentBenchX."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class TaskBase(BaseModel):
    """Base task model."""
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable task name")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed task description")
    instructions: str = Field(..., min_length=1, description="Instructions for the agent to follow")
    expected_outcome: Optional[str] = Field(None, description="Expected outcome or success criteria")
    allowed_tools: List[str] = Field(default_factory=list, description="List of tool names the agent is allowed to use")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints on task execution")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Model for updating a task."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, min_length=1)
    expected_outcome: Optional[str] = Field(None)
    allowed_tools: Optional[List[str]] = Field(None)
    constraints: Optional[Dict[str, Any]] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(None)


class TaskInDBBase(TaskBase):
    """Base task model as stored in database."""
    id: str = Field(..., description="Unique task identifier")
    version: str = Field(..., description="Task version")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @validator('id')
    def id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Task ID must not be empty')
        return v.strip()

    @validator('version')
    def version_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Task version must not be empty')
        return v.strip()


class Task(TaskInDBBase):
    """Complete task model."""
    pass


class TaskInDB(TaskInDBBase):
    """Task model as stored in database (includes any database-specific fields)."""
    pass


# Example task for testing
def create_example_task() -> Task:
    """Create an example task for testing purposes."""
    return Task(
        id="example-task-001",
        version="1.0.0",
        name="Simple Calculation Task",
        description="A task that asks the agent to perform a simple arithmetic calculation",
        instructions="Calculate the result of 15 + 27 and return just the number",
        expected_outcome="42",
        allowed_tools=["calculator"],
        constraints={"max_steps": 5, "timeout_seconds": 30},
        metadata={"category": "arithmetic", "difficulty": "easy"}
    )