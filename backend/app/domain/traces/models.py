"""Trace domain models for AgentBenchX."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import uuid4
import time
from enum import Enum


class TraceEventType(str, Enum):
    """Types of trace events that can be recorded."""
    TASK_STARTED = "TASK_STARTED"
    AGENT_STARTED = "AGENT_STARTED"
    ACTION_REQUESTED = "ACTION_REQUESTED"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    ERROR = "ERROR"
    ENVIRONMENT_RESET = "ENVIRONMENT_RESET"
    ENVIRONMENT_INITIALIZED = "ENVIRONMENT_INITIALIZED"


class TraceEventBase(BaseModel):
    """Base trace event model."""
    event_type: TraceEventType = Field(..., description="Type of trace event")
    timestamp: float = Field(default_factory=time.time, description="When the event occurred")
    sequence_number: int = Field(..., description="Sequence number of the event within the trace")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")


class TraceEventInDBBase(TraceEventBase):
    """Base trace event model as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique trace event identifier")
    trace_id: str = Field(..., description="ID of the trace this event belongs to")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class TraceEvent(TraceEventBase):
    """Complete trace event model (for in-memory use)."""
    pass


class TraceEventInDB(TraceEventInDBBase):
    """Trace event model as stored in database."""
    pass


class TraceEventCreate(TraceEventBase):
    """Model for creating a new trace event (for in-memory use)."""
    pass


class TraceBase(BaseModel):
    """Base trace model."""
    agent_id: str = Field(..., description="ID of the agent that generated this trace")
    task_id: str = Field(..., description="ID of the task being performed")
    environment_id: str = Field(..., description="ID of the environment where execution occurred")
    status: str = Field(..., description="Final status of the execution (e.g., SUCCESS, FAILED)")


class TraceCreate(TraceBase):
    """Model for creating a new trace."""
    pass


class TraceUpdate(BaseModel):
    """Model for updating a trace."""
    status: Optional[str] = Field(None, description="Final status of the execution")


class TraceInDBBase(TraceBase):
    """Base trace model as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique trace identifier")
    run_id: str = Field(..., description="ID of the execution run this trace belongs to")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When the trace started")
    ended_at: Optional[datetime] = Field(None, description="When the trace ended")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")


class TraceInDB(TraceInDBBase):
    """Complete trace model as stored in database."""
    events: List[TraceEvent] = Field(default_factory=list, description="List of trace events in chronological order")


class Trace(TraceBase):
    """Complete trace model (for in-memory use)."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique trace identifier")
    run_id: str = Field(default_factory=lambda: str(uuid4()), description="ID of the execution run this trace belongs to")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When the trace started")
    ended_at: Optional[datetime] = Field(None, description="When the trace ended")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")
    events: List[TraceEvent] = Field(default_factory=list, description="List of trace events in chronological order")

    def add_event(self, event: TraceEvent) -> None:
        """Add an event to the trace, maintaining chronological order."""
        # Set sequence number based on current length
        event.sequence_number = len(self.events)
        self.events.append(event)

    def get_events_by_type(self, event_type: TraceEventType) -> List[TraceEvent]:
        """Get all events of a specific type."""
        return [event for event in self.events if event.event_type == event_type]

    def get_latest_event(self) -> Optional[TraceEvent]:
        """Get the most recent event in the trace."""
        if self.events:
            return self.events[-1]
        return None


# Helper functions for creating common trace events
def create_task_started_event(task_id: str, task_name: str, metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create a TASK_STARTED trace event."""
    return TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "task_id": task_id,
            "task_name": task_name
        },
        metadata=metadata or {}
    )


def create_agent_started_event(agent_id: str, agent_type: str, metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create an AGENT_STARTED trace event."""
    return TraceEvent(
        event_type=TraceEventType.AGENT_STARTED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "agent_id": agent_id,
            "agent_type": agent_type
        },
        metadata=metadata or {}
    )


def create_action_requested_event(action_id: str, tool_name: str, arguments: Dict[str, Any],
                                metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create an ACTION_REQUESTED trace event."""
    return TraceEvent(
        event_type=TraceEventType.ACTION_REQUESTED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "action_id": action_id,
            "tool_name": tool_name,
            "arguments": arguments
        },
        metadata=metadata or {}
    )


def create_tool_executed_event(action_id: str, tool_name: str, success: bool,
                             output: Any = None, error: Optional[str] = None,
                             execution_time: float = 0.0,
                             metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create a TOOL_EXECUTED trace event."""
    return TraceEvent(
        event_type=TraceEventType.TOOL_EXECUTED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "action_id": action_id,
            "tool_name": tool_name,
            "success": success,
            "output": output,
            "error": error,
            "execution_time": execution_time
        },
        metadata=metadata or {}
    )


def create_action_completed_event(action_id: str, success: bool,
                                output: Any = None, error: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create an ACTION_COMPLETED trace event."""
    return TraceEvent(
        event_type=TraceEventType.ACTION_COMPLETED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "action_id": action_id,
            "success": success,
            "output": output,
            "error": error
        },
        metadata=metadata or {}
    )


def create_agent_completed_event(agent_id: str, success: bool,
                               output: Any = None, error: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create an AGENT_COMPLETED trace event."""
    return TraceEvent(
        event_type=TraceEventType.AGENT_COMPLETED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "agent_id": agent_id,
            "success": success,
            "output": output,
            "error": error
        },
        metadata=metadata or {}
    )


def create_task_completed_event(task_id: str, success: bool,
                              output: Any = None, error: Optional[str] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create a TASK_COMPLETED trace event."""
    return TraceEvent(
        event_type=TraceEventType.TASK_COMPLETED,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "task_id": task_id,
            "success": success,
            "output": output,
            "error": error
        },
        metadata=metadata or {}
    )


def create_error_event(error_message: str, error_type: str = "UNKNOWN",
                     metadata: Optional[Dict[str, Any]] = None) -> TraceEvent:
    """Create an ERROR trace event."""
    return TraceEvent(
        event_type=TraceEventType.ERROR,
        timestamp=time.time(),
        sequence_number=0,  # Will be overwritten when added to trace
        payload={
            "error_message": error_message,
            "error_type": error_type
        },
        metadata=metadata or {}
    )


class ActionExecution(BaseModel):
    """Represents a single action execution in the context."""
    action_id: str = Field(..., description="ID of the action that was executed")
    tool_name: str = Field(..., description="Name of the tool that was executed")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to the tool")
    result: Dict[str, Any] = Field(..., description="Result of the action execution")
    timestamp: float = Field(default_factory=time.time, description="When the action was executed")


class ExecutionContext(BaseModel):
    """Context provided to agents during execution, containing execution history."""
    run_id: str = Field(..., description="ID of the execution run")
    task_id: str = Field(..., description="ID of the task being executed")
    step: int = Field(..., description="Current step number (0-indexed)")
    available_tools: List[Dict[str, Any]] = Field(..., description="Tools available to the agent")
    history: List[ActionExecution] = Field(default_factory=list, description="History of action executions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")