"""Tests for the Tool and Action domain models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
import time

from backend.app.domain.tools.models import Tool, ToolCreate, ToolUpdate, Action, ActionResult


def test_tool_creation_valid():
    """Test creating a valid tool."""
    tool = Tool(
        name="calculator",
        description="Performs basic arithmetic operations",
        input_schema={
            "type": "object",
            "properties": {
                "operation": {"type": "string"},
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": "number"}
            }
        },
        is_safe=True,
        categories=["math", "arithmetic"],
        version="1.0.0"
    )

    assert tool.name == "calculator"
    assert tool.description == "Performs basic arithmetic operations"
    assert tool.input_schema["type"] == "object"
    assert tool.output_schema["type"] == "object"
    assert tool.is_safe == True
    assert tool.categories == ["math", "arithmetic"]
    assert tool.id is not None  # UUID should be generated
    assert tool.version == "1.0.0"
    assert isinstance(tool.created_at, datetime)
    assert isinstance(tool.updated_at, datetime)


def test_tool_creation_minimal():
    """Test creating a tool with only required fields."""
    tool = Tool(
        name="echo",
        description="Echoes input",
        input_schema={"type": "object", "properties": {"msg": {"type": "string"}}},
        version="1.0.0"
    )

    assert tool.name == "echo"
    assert tool.description == "Echoes input"
    assert tool.input_schema["type"] == "object"
    assert tool.output_schema is None
    assert tool.is_safe == True  # default
    assert tool.categories == []  # default
    assert tool.id is not None
    assert tool.version == "1.0.0"


def test_tool_name_validation():
    """Test tool name validation."""
    # Too short
    with pytest.raises(ValidationError):
        Tool(
            name="",
            description="Test tool",
            input_schema={"type": "object"}
        )

    # Too long
    with pytest.raises(ValidationError):
        Tool(
            name="x" * 101,
            description="Test tool",
            input_schema={"type": "object"}
        )


def test_tool_description_validation():
    """Test tool description validation."""
    # Too long
    with pytest.raises(ValidationError):
        Tool(
            name="test",
            description="x" * 501,
            input_schema={"type": "object"}
        )


def test_tool_serialization():
    """Test tool serialization to dict and JSON."""
    tool = Tool(
        name="serial-tool",
        description="Serialization test tool",
        input_schema={"type": "object", "properties": {"input": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"output": {"type": "string"}}},
        is_safe=False,
        categories=["test", "serialization"],
        version="1.0.0"
    )

    # Test dict serialization
    tool_dict = tool.model_dump()
    assert tool_dict["name"] == "serial-tool"
    assert tool_dict["description"] == "Serialization test tool"
    assert tool_dict["is_safe"] == False
    assert tool_dict["categories"] == ["test", "serialization"]

    # Test JSON serialization
    tool_json = tool.model_dump_json()
    assert "serial-tool" in tool_json
    assert "Serialization test tool" in tool_json


def test_tool_update():
    """Test updating a tool."""
    update_data = ToolUpdate(
        name="Updated Tool",
        description="Updated description",
        is_safe=False
    )

    assert update_data.name == "Updated Tool"
    assert update_data.description == "Updated description"
    assert update_data.input_schema is None
    assert update_data.output_schema is None
    assert update_data.is_safe == False
    assert update_data.categories is None


def test_action_creation():
    """Test creating an action."""
    action = Action(
        tool_name="calculator",
        arguments={"operation": "add", "a": 15, "b": 27}
    )

    assert action.tool_name == "calculator"
    assert action.arguments == {"operation": "add", "a": 15, "b": 27}
    assert action.action_id is not None  # UUID should be generated
    assert isinstance(action.timestamp, float)
    assert action.metadata == {}


def test_action_creation_with_metadata():
    """Test creating an action with metadata."""
    action = Action(
        tool_name="echo",
        arguments={"message": "hello"},
        metadata={"source": "test", "priority": "high"}
    )

    assert action.tool_name == "echo"
    assert action.arguments == {"message": "hello"}
    assert action.action_id is not None
    assert isinstance(action.timestamp, float)
    assert action.metadata == {"source": "test", "priority": "high"}


def test_action_name_validation():
    """Test action tool_name validation."""
    # Empty name
    with pytest.raises(ValidationError):
        Action(
            tool_name="",
            arguments={"arg": "value"}
        )

    # Valid name
    action = Action(
        tool_name="valid_tool",
        arguments={"arg": "value"}
    )
    assert action.tool_name == "valid_tool"


def test_action_result_creation():
    """Test creating an action result."""
    result = ActionResult(
        success=True,
        output=42,
        execution_time=0.5
    )

    assert result.success == True
    assert result.output == 42
    assert result.error is None
    assert result.execution_time == 0.5
    assert result.state_change is None
    assert result.metadata == {}


def test_action_result_creation_with_error():
    """Test creating an action result with an error."""
    result = ActionResult(
        success=False,
        output=None,
        error="Something went wrong",
        execution_time=1.2,
        state_change={"key": "value"},
        metadata={"attempt": 1}
    )

    assert result.success == False
    assert result.output is None
    assert result.error == "Something went wrong"
    assert result.execution_time == 1.2
    assert result.state_change == {"key": "value"}
    assert result.metadata == {"attempt": 1}


def test_action_result_success_false_with_output():
    """Test that an action result can have success=False but still have output."""
    result = ActionResult(
        success=False,
        output="Partial output",
        error="Timed out",
        execution_time=2.0
    )

    assert result.success == False
    assert result.output == "Partial output"
    assert result.error == "Timed out"