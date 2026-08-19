"""Tests for ExecutionContext and ActionExecution models."""

import pytest
from pydantic import ValidationError
from backend.app.domain.traces.models import ExecutionContext, ActionExecution


def test_execution_context_creation_valid():
    """Test creating a valid execution context."""
    context = ExecutionContext(
        run_id="test-run-001",
        task_id="test-task-001",
        step=0,
        available_tools=[
            {
                "name": "calculator",
                "description": "Performs basic arithmetic",
                "input_schema": {"type": "object", "properties": {"a": {"type": "number"}}}
            }
        ],
        history=[],
        metadata={"test": "metadata"}
    )

    assert context.run_id == "test-run-001"
    assert context.task_id == "test-task-001"
    assert context.step == 0
    assert len(context.available_tools) == 1
    assert context.available_tools[0]["name"] == "calculator"
    assert len(context.history) == 0
    assert context.metadata == {"test": "metadata"}


def test_execution_context_creation_minimal():
    """Test creating an execution context with minimal fields."""
    context = ExecutionContext(
        run_id="test-run-001",
        task_id="test-task-001",
        step=0,
        available_tools=[]
    )

    assert context.run_id == "test-run-001"
    assert context.task_id == "test-task-001"
    assert context.step == 0
    assert context.available_tools == []
    assert context.history == []  # default factory
    assert context.metadata == {}  # default factory


def test_execution_context_step_validation():
    """Test that step must be an integer."""
    with pytest.raises(ValidationError):
        ExecutionContext(
            run_id="test-run-001",
            task_id="test-task-001",
            step="invalid",  # Should be integer
            available_tools=[]
        )


def test_action_execution_creation_valid():
    """Test creating a valid action execution."""
    action_execution = ActionExecution(
        action_id="test-action-001",
        tool_name="calculator",
        arguments={"operation": "add", "a": 1, "b": 2},
        result={"success": True, "output": 3, "error": None},
        timestamp=1234567890.0
    )

    assert action_execution.action_id == "test-action-001"
    assert action_execution.tool_name == "calculator"
    assert action_execution.arguments == {"operation": "add", "a": 1, "b": 2}
    assert action_execution.result == {"success": True, "output": 3, "error": None}
    assert action_execution.timestamp == 1234567890.0


def test_action_execution_creation_minimal():
    """Test creating an action execution with minimal fields."""
    action_execution = ActionExecution(
        action_id="test-action-001",
        tool_name="calculator",
        arguments={"operation": "add"},
        result={"success": True}
    )

    assert action_execution.action_id == "test-action-001"
    assert action_execution.tool_name == "calculator"
    assert action_execution.arguments == {"operation": "add"}
    assert action_execution.result == {"success": True}
    # timestamp should be set by default factory


def test_execution_context_serialization():
    """Test that execution context can be serialized to dict and JSON."""
    context = ExecutionContext(
        run_id="test-run-001",
        task_id="test-task-001",
        step=1,
        available_tools=[
            {"name": "calculator", "description": "A calculator tool"}
        ],
        history=[
            {
                "action_id": "action-001",
                "tool_name": "calculator",
                "arguments": {"a": 1, "b": 2},
                "result": {"success": True, "output": 3},
                "timestamp": 1234567890.0
            }
        ],
        metadata={"test": "value"}
    )

    # Test dict serialization
    context_dict = context.model_dump()
    assert context_dict["run_id"] == "test-run-001"
    assert context_dict["task_id"] == "test-task-001"
    assert context_dict["step"] == 1
    assert len(context_dict["available_tools"]) == 1
    assert len(context_dict["history"]) == 1
    assert context_dict["metadata"] == {"test": "value"}

    # Test JSON serialization
    context_json = context.model_dump_json()
    assert "test-run-001" in context_json
    assert "test-task-001" in context_json
    assert "calculator" in context_json


def test_execution_context_with_action_history():
    """Test execution context with action history."""
    action_executions = [
        ActionExecution(
            action_id="action-001",
            tool_name="calculator",
            arguments={"operation": "add", "a": 1, "b": 2},
            result={"success": True, "output": 3, "error": None},
            timestamp=1234567890.0
        ),
        ActionExecution(
            action_id="action-002",
            tool_name="calculator",
            arguments={"operation": "multiply", "a": 3, "b": 4},
            result={"success": True, "output": 12, "error": None},
            timestamp=1234567891.0
        )
    ]

    context = ExecutionContext(
        run_id="test-run-001",
        task_id="test-task-001",
        step=2,
        available_tools=[],
        history=[action.model_dump() for action in action_executions],
        metadata={}
    )

    assert len(context.history) == 2
    assert context.history[0].action_id == "action-001"
    assert context.history[0].tool_name == "calculator"
    assert context.history[0].result["success"] == True
    assert context.history[1].action_id == "action-002"
    assert context.history[1].result["output"] == 12


if __name__ == "__main__":
    pytest.main([__file__])