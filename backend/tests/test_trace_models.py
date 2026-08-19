"""Tests for the Trace domain models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.app.domain.traces.models import (
    TraceEvent, Trace, TraceEventType,
    create_task_started_event, create_agent_started_event,
    create_action_requested_event, create_tool_executed_event,
    create_action_completed_event, create_agent_completed_event,
    create_task_completed_event, create_error_event
)


def test_trace_event_creation_valid():
    """Test creating a valid trace event."""
    event = TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-123", "task_name": "Test Task"},
        metadata={"source": "test"}
    )

    assert event.event_type == TraceEventType.TASK_STARTED
    assert event.timestamp == 1234567890.0
    assert event.sequence_number == 0
    assert event.payload["task_id"] == "task-123"
    assert event.payload["task_name"] == "Test Task"
    assert event.metadata["source"] == "test"
    # For in-memory TraceEvent, trace_id and created_at are not present


def test_trace_event_creation_minimal():
    """Test creating a trace event with only required fields."""
    event = TraceEvent(
        event_type=TraceEventType.ERROR,
        timestamp=1234567890.0,
        sequence_number=5
    )

    assert event.event_type == TraceEventType.ERROR
    assert event.timestamp == 1234567890.0
    assert event.sequence_number == 5
    assert event.payload == {}  # default
    assert event.metadata == {}  # default
    # For in-memory TraceEvent, trace_id and created_at are not present


def test_trace_event_sequence_number_validation():
    """Test that sequence number is required."""
    with pytest.raises(ValidationError):
        TraceEvent(
            event_type=TraceEventType.TASK_STARTED,
            timestamp=1234567890.0
            # missing sequence_number
        )


def test_trace_event_type_validation():
    """Test that event_type must be a valid TraceEventType."""
    # Valid type should work
    event = TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0
    )
    assert event.event_type == TraceEventType.TASK_STARTED

    # Invalid type should fail
    with pytest.raises(ValidationError):
        TraceEvent(
            event_type="INVALID_TYPE",
            timestamp=1234567890.0,
            sequence_number=0
        )


def test_trace_event_payload_and_metadata():
    """Test that payload and metadata can hold various data types."""
    event = TraceEvent(
        event_type=TraceEventType.TOOL_EXECUTED,
        timestamp=1234567890.0,
        sequence_number=10,
        payload={
            "action_id": "action-123",
            "tool_name": "calculator",
            "success": True,
            "output": 42,
            "execution_time": 0.123
        },
        metadata={
            "trace_id": "trace-456",
            "tags": ["math", "calculation"],
            "nested": {
                "inner": "value"
            }
        }
    )

    assert event.payload["output"] == 42
    assert event.payload["execution_time"] == 0.123
    assert event.metadata["tags"] == ["math", "calculation"]
    assert event.metadata["nested"]["inner"] == "value"


def test_trace_creation_valid():
    """Test creating a valid trace."""
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS"
    )

    assert trace.agent_id == "agent-123"
    assert trace.task_id == "task-456"
    assert trace.environment_id == "env-789"
    assert trace.status == "SUCCESS"
    assert trace.events == []  # default empty list
    assert trace.id is not None  # UUID should be generated
    assert trace.run_id is not None  # UUID should be generated
    assert isinstance(trace.started_at, datetime)
    # For in-memory Trace, trace_id, run_id, started_at, ended_at are present


def test_trace_add_event():
    """Test adding events to a trace."""
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS"
    )

    # Add first event
    event1 = TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,  # This will be overridden
        payload={"task_id": "task-456"}
    )
    trace.add_event(event1)

    assert len(trace.events) == 1
    assert trace.events[0].sequence_number == 0  # Should be set to 0
    assert trace.events[0].event_type == TraceEventType.TASK_STARTED

    # Add second event
    event2 = TraceEvent(
        event_type=TraceEventType.AGENT_STARTED,
        timestamp=1234567891.0,
        sequence_number=999,  # This will be overridden
        payload={"agent_id": "agent-123"}
    )
    trace.add_event(event2)

    assert len(trace.events) == 2
    assert trace.events[1].sequence_number == 1  # Should be set to 1
    assert trace.events[1].event_type == TraceEventType.AGENT_STARTED


def test_trace_get_events_by_type():
    """Test filtering events by type."""
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS"
    )

    # Add mixed events
    trace.add_event(TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-456"}
    ))
    trace.add_event(TraceEvent(
        event_type=TraceEventType.AGENT_STARTED,
        timestamp=1234567891.0,
        sequence_number=1,
        payload={"agent_id": "agent-123"}
    ))
    trace.add_event(TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567892.0,
        sequence_number=2,
        payload={"task_id": "task-456", "attempt": 2}
    ))
    trace.add_event(TraceEvent(
        event_type=TraceEventType.TOOL_EXECUTED,
        timestamp=1234567893.0,
        sequence_number=3,
        payload={"tool_name": "calculator"}
    ))

    # Get all TASK_STARTED events
    task_started_events = trace.get_events_by_type(TraceEventType.TASK_STARTED)
    assert len(task_started_events) == 2
    assert all(event.event_type == TraceEventType.TASK_STARTED for event in task_started_events)
    assert task_started_events[0].payload["task_id"] == "task-456"
    assert task_started_events[1].payload["attempt"] == 2

    # Get all AGENT_STARTED events
    agent_started_events = trace.get_events_by_type(TraceEventType.AGENT_STARTED)
    assert len(agent_started_events) == 1
    assert agent_started_events[0].payload["agent_id"] == "agent-123"

    # Get all TOOL_EXECUTED events
    tool_executed_events = trace.get_events_by_type(TraceEventType.TOOL_EXECUTED)
    assert len(tool_executed_events) == 1
    assert tool_executed_events[0].payload["tool_name"] == "calculator"

    # Get non-existent event type
    error_events = trace.get_events_by_type(TraceEventType.ERROR)
    assert len(error_events) == 0


def test_trace_get_latest_event():
    """Test getting the latest event from a trace."""
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS"
    )

    # Initially no events
    assert trace.get_latest_event() is None

    # Add events
    event1 = TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-456"}
    )
    trace.add_event(event1)

    latest = trace.get_latest_event()
    assert latest == event1

    event2 = TraceEvent(
        event_type=TraceEventType.AGENT_STARTED,
        timestamp=1234567891.0,
        sequence_number=1,
        payload={"agent_id": "agent-123"}
    )
    trace.add_event(event2)

    latest = trace.get_latest_event()
    assert latest == event2
    assert latest.event_type == TraceEventType.AGENT_STARTED


def test_create_task_started_event():
    """Test the helper function for creating a TASK_STARTED event."""
    event = create_task_started_event(
        task_id="task-123",
        task_name="Test Task",
        metadata={"priority": "high"}
    )

    assert event.event_type == TraceEventType.TASK_STARTED
    assert event.payload["task_id"] == "task-123"
    assert event.payload["task_name"] == "Test Task"
    assert event.metadata["priority"] == "high"


def test_create_agent_started_event():
    """Test the helper function for creating an AGENT_STARTED event."""
    event = create_agent_started_event(
        agent_id="agent-456",
        agent_type="MockAgent",
        metadata={"version": "1.0.0"}
    )

    assert event.event_type == TraceEventType.AGENT_STARTED
    assert event.payload["agent_id"] == "agent-456"
    assert event.payload["agent_type"] == "MockAgent"
    assert event.metadata["version"] == "1.0.0"


def test_create_action_requested_event():
    """Test the helper function for creating an ACTION_REQUESTED event."""
    event = create_action_requested_event(
        action_id="action-789",
        tool_name="calculator",
        arguments={"operation": "add", "a": 10, "b": 5},
        metadata={"requested_by": "test-agent"}
    )

    assert event.event_type == TraceEventType.ACTION_REQUESTED
    assert event.payload["action_id"] == "action-789"
    assert event.payload["tool_name"] == "calculator"
    assert event.payload["arguments"] == {"operation": "add", "a": 10, "b": 5}
    assert event.metadata["requested_by"] == "test-agent"


def test_create_tool_executed_event():
    """Test the helper function for creating a TOOL_EXECUTED event."""
    event = create_tool_executed_event(
        action_id="action-789",
        tool_name="calculator",
        success=True,
        output=15,
        execution_time=0.05,
        metadata={"cached": False}
    )

    assert event.event_type == TraceEventType.TOOL_EXECUTED
    assert event.payload["action_id"] == "action-789"
    assert event.payload["tool_name"] == "calculator"
    assert event.payload["success"] == True
    assert event.payload["output"] == 15
    assert event.payload["execution_time"] == 0.05
    assert event.metadata["cached"] == False


def test_create_tool_executed_event_failure():
    """Test the helper function for creating a failed TOOL_EXECUTED event."""
    event = create_tool_executed_event(
        action_id="action-789",
        tool_name="calculator",
        success=False,
        error="Division by zero",
        execution_time=0.01
    )

    assert event.event_type == TraceEventType.TOOL_EXECUTED
    assert event.payload["action_id"] == "action-789"
    assert event.payload["tool_name"] == "calculator"
    assert event.payload["success"] == False
    assert event.payload["error"] == "Division by zero"
    assert event.payload["execution_time"] == 0.01


def test_create_action_completed_event():
    """Test the helper function for creating an ACTION_COMPLETED event."""
    event = create_action_completed_event(
        action_id="action-789",
        success=True,
        output=42,
        metadata={"source": "calculator"}
    )

    assert event.event_type == TraceEventType.ACTION_COMPLETED
    assert event.payload["action_id"] == "action-789"
    assert event.payload["success"] == True
    assert event.payload["output"] == 42
    assert event.metadata["source"] == "calculator"


def test_create_agent_completed_event():
    """Test the helper function for creating an AGENT_COMPLETED event."""
    event = create_agent_completed_event(
        agent_id="agent-123",
        success=False,
        error="Timeout",
        metadata={"duration": 30.0}
    )

    assert event.event_type == TraceEventType.AGENT_COMPLETED
    assert event.payload["agent_id"] == "agent-123"
    assert event.payload["success"] == False
    assert event.payload["error"] == "Timeout"
    assert event.metadata["duration"] == 30.0


def test_create_task_completed_event():
    """Test the helper function for creating a TASK_COMPLETED event."""
    event = create_task_completed_event(
        task_id="task-456",
        success=True,
        output="Task completed successfully",
        metadata={"steps_taken": 3}
    )

    assert event.event_type == TraceEventType.TASK_COMPLETED
    assert event.payload["task_id"] == "task-456"
    assert event.payload["success"] == True
    assert event.payload["output"] == "Task completed successfully"
    assert event.metadata["steps_taken"] == 3


def test_create_error_event():
    """Test the helper function for creating an ERROR event."""
    event = create_error_event(
        error_message="Invalid input provided",
        error_type="VALIDATION_ERROR",
        metadata={"input": "bad data", "field": "task_instructions"}
    )

    assert event.event_type == TraceEventType.ERROR
    assert event.payload["error_message"] == "Invalid input provided"
    assert event.payload["error_type"] == "VALIDATION_ERROR"
    assert event.metadata["input"] == "bad data"
    assert event.metadata["field"] == "task_instructions"


def test_trace_event_serialization():
    """Test trace event serialization to dict and JSON."""
    event = TraceEvent(
        event_type=TraceEventType.TOOL_EXECUTED,
        timestamp=1234567890.5,
        sequence_number=42,
        payload={
            "action_id": "action-123",
            "tool_name": "calculator",
            "success": True,
            "output": 42
        },
        metadata={"trace_id": "trace-456"}
    )

    # Test dict serialization
    event_dict = event.model_dump()
    assert event_dict["event_type"] == TraceEventType.TOOL_EXECUTED
    assert event_dict["timestamp"] == 1234567890.5
    assert event_dict["sequence_number"] == 42
    assert event_dict["payload"]["output"] == 42
    assert event_dict["metadata"]["trace_id"] == "trace-456"

    # Test JSON serialization
    event_json = event.model_dump_json()
    assert TraceEventType.TOOL_EXECUTED in event_json
    assert "1234567890.5" in event_json
    assert "action-123" in event_json
    assert "calculator" in event_json
    assert "42" in event_json  # output


def test_trace_serialization():
    """Test trace serialization to dict and JSON."""
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS"
    )

    # Add an event
    trace.add_event(TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-456"}
    ))

    # Test dict serialization
    trace_dict = trace.model_dump()
    assert trace_dict["agent_id"] == "agent-123"
    assert trace_dict["task_id"] == "task-456"
    assert trace_dict["environment_id"] == "env-789"
    assert trace_dict["status"] == "SUCCESS"
    assert len(trace_dict["events"]) == 1
    assert trace_dict["events"][0]["payload"]["task_id"] == "task-456"

    # Test JSON serialization
    trace_json = trace.model_dump_json()
    assert "agent-123" in trace_json
    assert "task-456" in trace_json
    assert "env-789" in trace_json
    assert "SUCCESS" in trace_json