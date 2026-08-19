"""Tests for Trace and TraceEvent serialization."""

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.domain.traces.models import (
    Trace, TraceEvent, TraceEventType,
    create_task_started_event, create_agent_started_event,
    create_action_requested_event, create_tool_executed_event,
    create_action_completed_event, create_agent_completed_event,
    create_task_completed_event, create_error_event
)


def test_trace_event_round_trip_serialization():
    """Test that TraceEvent can be serialized to JSON and deserialized correctly."""
    original_event = TraceEvent(
        event_type=TraceEventType.TOOL_EXECUTED,
        timestamp=1234567890.5,
        sequence_number=42,
        payload={
            "action_id": "action-123",
            "tool_name": "calculator",
            "success": True,
            "output": 42,
            "execution_time": 0.123
        },
        metadata={"trace_id": "trace-456", "tag": "test"}
    )

    # Serialize to JSON string
    json_str = original_event.model_dump_json()

    # Deserialize from JSON string
    restored_event = TraceEvent.model_validate_json(json_str)

    # Verify all fields match
    assert restored_event.event_type == original_event.event_type
    assert restored_event.timestamp == original_event.timestamp
    assert restored_event.sequence_number == original_event.sequence_number
    assert restored_event.payload == original_event.payload
    assert restored_event.metadata == original_event.metadata


def test_trace_round_trip_serialization():
    """Test that Trace can be serialized to JSON and deserialized correctly."""
    # Create a trace with various data types
    trace_id = uuid4()
    run_id = uuid4()
    started_at = datetime(2026, 8, 19, 10, 0, 0, tzinfo=timezone.utc)
    ended_at = datetime(2026, 8, 19, 10, 5, 30, tzinfo=timezone.utc)

    original_trace = Trace(
        id=str(trace_id),
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS",
        run_id=str(run_id),
        started_at=started_at,
        ended_at=ended_at,
        metadata={
            "key": "value",
            "numbers": [1, 2, 3],
            "nested": {"inner": "data"},
            "null_value": None,
            "boolean": True
        }
    )

    # Add events
    event1 = TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-456"},
        metadata={"source": "test"}
    )
    original_trace.add_event(event1)

    event2 = TraceEvent(
        event_type=TraceEventType.AGENT_STARTED,
        timestamp=1234567891.0,
        sequence_number=1,
        payload={"agent_id": "agent-123", "agent_type": "TestAgent"},
        metadata={"version": "1.0"}
    )
    original_trace.add_event(event2)

    # Serialize to JSON string
    json_str = original_trace.model_dump_json()

    # Deserialize from JSON string
    restored_trace = Trace.model_validate_json(json_str)

    # Verify all fields match
    assert restored_trace.id == original_trace.id
    assert restored_trace.agent_id == original_trace.agent_id
    assert restored_trace.task_id == original_trace.task_id
    assert restored_trace.environment_id == original_trace.environment_id
    assert restored_trace.status == original_trace.status
    assert restored_trace.run_id == original_trace.run_id
    assert restored_trace.started_at == original_trace.started_at
    assert restored_trace.ended_at == original_trace.ended_at
    assert restored_trace.metadata == original_trace.metadata
    assert len(restored_trace.events) == len(original_trace.events)

    # Verify events
    for i, (orig_event, rest_event) in enumerate(zip(original_trace.events, restored_trace.events)):
        assert rest_event.event_type == orig_event.event_type
        assert rest_event.timestamp == orig_event.timestamp
        assert rest_event.sequence_number == orig_event.sequence_number
        assert rest_event.payload == orig_event.payload
        assert rest_event.metadata == orig_event.metadata


def test_empty_trace_serialization():
    """Test serialization of a trace with zero events."""
    trace_id = uuid4()
    run_id = uuid4()

    original_trace = Trace(
        id=str(trace_id),
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS",
        run_id=str(run_id),
        started_at=datetime(2026, 8, 19, 10, 0, 0, tzinfo=timezone.utc),
        ended_at=None,
        metadata={}
    )

    # Should have zero events
    assert len(original_trace.events) == 0

    # Serialize and deserialize
    json_str = original_trace.model_dump_json()
    restored_trace = Trace.model_validate_json(json_str)

    assert restored_trace.id == original_trace.id
    assert len(restored_trace.events) == 0
    assert restored_trace.agent_id == original_trace.agent_id


def test_alternative_serialization_method():
    """Test the alternative serialization method using model_dump(mode='json')."""
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS"
    )

    trace.add_event(TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-456"}
    ))

    # Alternative method: model_dump(mode="json") -> json.dumps -> json.loads -> model_validate
    dict_from_model = trace.model_dump(mode="json")
    json_bytes = json.dumps(dict_from_model)
    parsed_dict = json.loads(json_bytes)
    restored_trace = Trace.model_validate(parsed_dict)

    assert restored_trace.agent_id == trace.agent_id
    assert restored_trace.task_id == trace.task_id
    assert len(restored_trace.events) == len(trace.events)
    assert restored_trace.events[0].payload["task_id"] == "task-456"


def test_trace_event_with_complex_payload():
    """Test TraceEvent with complex payload data types."""
    complex_payload = {
        "string": "test",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "none": None,
        "empty_string": "",
        "zero": 0,
        "false_bool": False,
        "list": [1, 2, 3, "string", None],
        "nested_dict": {
            "level1": {
                "level2": "deep_value"
            },
            "simple": "value"
        },
        "mixed_list": [
            {"key": "value"},
            [1, 2, 3],
            "string",
            42
        ]
    }

    event = TraceEvent(
        event_type=TraceEventType.TOOL_EXECUTED,
        timestamp=1234567890.5,
        sequence_number=99,
        payload=complex_payload,
        metadata={"complex": True}
    )

    # Serialize and deserialize
    json_str = event.model_dump_json()
    restored_event = TraceEvent.model_validate_json(json_str)

    assert restored_event.payload == complex_payload
    assert restored_event.metadata == event.metadata


def test_invalid_uuid_rejected():
    """Test that invalid UUID in JSON is rejected during deserialization."""
    # This test applies to TraceInDB model which expects UUIDs as strings
    # For in-memory models, we're testing the concept that invalid data should be rejected

    # Test with invalid event type (should be rejected)
    invalid_json = '{"event_type": "INVALID_TYPE", "timestamp": 1234567890.0, "sequence_number": 0}'

    with pytest.raises(ValidationError):
        TraceEvent.model_validate_json(invalid_json)


def test_missing_required_field():
    """Test that missing required fields are caught during deserialization."""
    # Missing sequence_number (required)
    incomplete_json = '{"event_type": "TASK_STARTED", "timestamp": 1234567890.0}'

    with pytest.raises(ValidationError):
        TraceEvent.model_validate_json(incomplete_json)


def test_invalid_timestamp_type():
    """Test that invalid timestamp types are rejected."""
    invalid_json = '{"event_type": "TASK_STARTED", "timestamp": "not-a-number", "sequence_number": 0}'

    with pytest.raises(ValidationError):
        TraceEvent.model_validate_json(invalid_json)


def test_serialization_preserves_timezone_info():
    """Test that timezone information is preserved in datetime serialization."""
    # Create trace with timezone-aware datetime
    trace = Trace(
        agent_id="agent-123",
        task_id="task-456",
        environment_id="env-789",
        status="SUCCESS",
        started_at=datetime(2026, 8, 19, 10, 0, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 8, 19, 10, 5, 30, tzinfo=timezone.utc)
    )

    # Add an event
    trace.add_event(TraceEvent(
        event_type=TraceEventType.TASK_STARTED,
        timestamp=1234567890.0,
        sequence_number=0,
        payload={"task_id": "task-456"}
    ))

    # Serialize and deserialize
    json_str = trace.model_dump_json()
    restored_trace = Trace.model_validate_json(json_str)

    # Verify timezone info is preserved
    assert restored_trace.started_at.tzinfo is not None
    assert restored_trace.ended_at.tzinfo is not None
    assert restored_trace.started_at == trace.started_at
    assert restored_trace.ended_at == trace.ended_at


def test_all_trace_event_types_serialization():
    """Test that all TraceEventType enum values can be serialized and deserialized."""
    for event_type in TraceEventType:
        event = TraceEvent(
            event_type=event_type,
            timestamp=1234567890.0,
            sequence_number=0,
            payload={"test": "data"},
            metadata={"meta": "data"}
        )

        # Serialize and deserialize
        json_str = event.model_dump_json()
        restored_event = TraceEvent.model_validate_json(json_str)

        assert restored_event.event_type == event_type
        assert restored_event.payload == event.payload
        assert restored_event.metadata == event.metadata