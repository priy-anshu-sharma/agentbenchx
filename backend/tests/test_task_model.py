"""Tests for the Task domain model."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.app.domain.tasks.models import Task, TaskCreate, TaskUpdate, create_example_task


def test_task_creation_valid():
    """Test creating a valid task."""
    task = Task(
        id="test-task-001",
        version="1.0.0",
        name="Test Task",
        description="A test task",
        instructions="Do something",
        expected_outcome="Success",
        allowed_tools=["tool1", "tool2"],
        constraints={"max_steps": 10},
        metadata={"category": "test"}
    )

    assert task.id == "test-task-001"
    assert task.version == "1.0.0"
    assert task.name == "Test Task"
    assert task.description == "A test task"
    assert task.instructions == "Do something"
    assert task.expected_outcome == "Success"
    assert task.allowed_tools == ["tool1", "tool2"]
    assert task.constraints == {"max_steps": 10}
    assert task.metadata == {"category": "test"}
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_creation_minimal():
    """Test creating a task with only required fields."""
    task = Task(
        id="minimal-task",
        version="1.0.0",
        name="Minimal Task",
        instructions="Do minimal"
    )

    assert task.id == "minimal-task"
    assert task.version == "1.0.0"
    assert task.name == "Minimal Task"
    assert task.instructions == "Do minimal"
    assert task.description is None
    assert task.expected_outcome is None
    assert task.allowed_tools == []
    assert task.constraints == {}
    assert task.metadata == {}


def test_task_id_validation():
    """Test that task ID cannot be empty."""
    with pytest.raises(ValidationError) as exc_info:
        Task(
            id="",
            version="1.0.0",
            name="Test Task",
            instructions="Do something"
        )
    assert "Task ID must not be empty" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Task(
            id="   ",
            version="1.0.0",
            name="Test Task",
            instructions="Do something"
        )
    assert "Task ID must not be empty" in str(exc_info.value)


def test_task_version_validation():
    """Test that task version cannot be empty."""
    with pytest.raises(ValidationError) as exc_info:
        Task(
            id="test-task",
            version="",
            name="Test Task",
            instructions="Do something"
        )
    assert "Task version must not be empty" in str(exc_info.value)


def test_task_name_validation():
    """Test task name validation."""
    # Too short
    with pytest.raises(ValidationError):
        Task(
            id="test-task",
            version="1.0.0",
            name="",
            instructions="Do something"
        )

    # Too long
    with pytest.raises(ValidationError):
        Task(
            id="test-task",
            version="1.0.0",
            name="x" * 201,
            instructions="Do something"
        )


def test_task_instructions_validation():
    """Test task instructions validation."""
    # Too short
    with pytest.raises(ValidationError):
        Task(
            id="test-task",
            version="1.0.0",
            name="Test Task",
            instructions=""
        )


def test_task_description_validation():
    """Test task description validation."""
    # Too long
    with pytest.raises(ValidationError):
        Task(
            id="test-task",
            version="1.0.0",
            name="Test Task",
            instructions="Do something",
            description="x" * 1001
        )


def test_task_serialization():
    """Test task serialization to dict and JSON."""
    task = Task(
        id="serial-task",
        version="1.0.0",
        name="Serialization Task",
        description="Test serialization",
        instructions="Serialize me",
        expected_outcome="Serialized",
        allowed_tools=["tool1"],
        constraints={"max_steps": 5},
        metadata={"test": True}
    )

    # Test dict serialization
    task_dict = task.model_dump()
    assert task_dict["id"] == "serial-task"
    assert task_dict["name"] == "Serialization Task"
    assert task_dict["allowed_tools"] == ["tool1"]
    assert task_dict["constraints"] == {"max_steps": 5}

    # Test JSON serialization
    task_json = task.model_dump_json()
    assert "serial-task" in task_json
    assert "Serialization Task" in task_json


def test_task_update():
    """Test updating a task."""
    update_data = TaskUpdate(
        name="Updated Task",
        description="Updated description",
        instructions="Updated instructions"
    )

    assert update_data.name == "Updated Task"
    assert update_data.description == "Updated description"
    assert update_data.instructions == "Updated instructions"
    assert update_data.expected_outcome is None
    assert update_data.allowed_tools is None
    assert update_data.constraints is None
    assert update_data.metadata is None


def test_create_example_task():
    """Test the example task creation function."""
    task = create_example_task()

    assert task.id == "example-task-001"
    assert task.version == "1.0.0"
    assert task.name == "Simple Calculation Task"
    assert task.instructions == "Calculate the result of 15 + 27 and return just the number"
    assert task.expected_outcome == "42"
    assert task.allowed_tools == ["calculator"]
    assert task.constraints == {"max_steps": 5, "timeout_seconds": 30}
    assert task.metadata == {"category": "arithmetic", "difficulty": "easy"}