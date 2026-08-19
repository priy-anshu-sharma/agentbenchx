"""Tests for the EvaluationRun domain model."""

import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError

from backend.app.domain.evaluations.models import (
    EvaluationRun,
    EvaluationRunCreate,
    EvaluationRunUpdate,
    EvaluationRunInDB,
    EvaluationResult,
    RunStatus
)


def test_evaluation_run_creation_valid():
    """Test creating a valid evaluation run."""
    run = EvaluationRun(
        task_id="task-123",
        task_version="1.0.0",
        agent_id="agent-456",
        agent_version="2.0.0",
        environment_id="env-789",
        trace_id="trace-abc",
        benchmark_id="bench-xyz",
        benchmark_version="1.0.0",
        status=RunStatus.COMPLETED,
        started_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        completed_at=datetime.now(timezone.utc),
        duration=10.0,
        configuration={"key": "value"},
        metadata={"test": "data"}
    )

    assert run.task_id == "task-123"
    assert run.task_version == "1.0.0"
    assert run.agent_id == "agent-456"
    assert run.agent_version == "2.0.0"
    assert run.environment_id == "env-789"
    assert run.trace_id == "trace-abc"
    assert run.benchmark_id == "bench-xyz"
    assert run.benchmark_version == "1.0.0"
    assert run.status == RunStatus.COMPLETED
    assert run.duration == 10.0
    assert run.configuration == {"key": "value"}
    assert run.metadata == {"test": "data"}
    assert isinstance(run.id, str)
    assert isinstance(run.created_at, datetime)
    assert isinstance(run.updated_at, datetime)


def test_evaluation_run_creation_minimal():
    """Test creating an evaluation run with only required fields."""
    run = EvaluationRun(
        task_id="task-123",
        task_version="1.0.0",
        agent_id="agent-456",
        agent_version="2.0.0",
        environment_id="env-789"
    )

    assert run.task_id == "task-123"
    assert run.task_version == "1.0.0"
    assert run.agent_id == "agent-456"
    assert run.agent_version == "2.0.0"
    assert run.environment_id == "env-789"
    assert run.trace_id is None
    assert run.benchmark_id is None
    assert run.benchmark_version is None
    assert run.status == RunStatus.PENDING  # default
    assert run.started_at is None  # default
    assert run.completed_at is None  # default
    assert run.duration is None  # default
    assert run.configuration == {}  # default
    assert run.metadata == {}  # default
    assert isinstance(run.id, str)
    # Timestamps should be set by default_factory
    assert isinstance(run.created_at, datetime)
    assert isinstance(run.updated_at, datetime)


def test_evaluation_run_create_model():
    """Test the EvaluationRunCreate model."""
    create_data = EvaluationRunCreate(
        task_id="task-123",
        task_version="1.0.0",
        agent_id="agent-456",
        agent_version="2.0.0",
        environment_id="env-789",
        trace_id="trace-abc",
        configuration={"test": True}
    )

    assert create_data.task_id == "task-123"
    assert create_data.task_version == "1.0.0"
    assert create_data.agent_id == "agent-456"
    assert create_data.agent_version == "2.0.0"
    assert create_data.environment_id == "env-789"
    assert create_data.trace_id == "trace-abc"
    assert create_data.configuration == {"test": True}
    # These should be None by default except metadata which defaults to empty dict
    assert create_data.benchmark_id is None
    assert create_data.benchmark_version is None
    assert create_data.metadata == {}


def test_evaluation_run_update_model():
    """Test the EvaluationRunUpdate model."""
    update_data = EvaluationRunUpdate(
        trace_id="trace-new",
        status=RunStatus.RUNNING,
        started_at=datetime.now(timezone.utc),
        duration=5.0
    )

    assert update_data.trace_id == "trace-new"
    assert update_data.status == RunStatus.RUNNING
    assert update_data.started_at is not None
    assert update_data.duration == 5.0
    # These should be None
    assert update_data.completed_at is None
    assert update_data.configuration is None
    assert update_data.metadata is None


def test_evaluation_run_in_db_model():
    """Test the EvaluationRunInDB model (database model)."""
    run_in_db = EvaluationRunInDB(
        task_id="task-123",
        task_version="1.0.0",
        agent_id="agent-456",
        agent_version="2.0.0",
        environment_id="env-789",
        trace_id="trace-abc",
        benchmark_id="bench-xyz",
        benchmark_version="1.0.0",
        status=RunStatus.COMPLETED,
        started_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        completed_at=datetime.now(timezone.utc),
        duration=10.0,
        configuration={"key": "value"},
        metadata={"test": "data"}
    )

    assert run_in_db.task_id == "task-123"
    assert run_in_db.task_version == "1.0.0"
    assert run_in_db.agent_id == "agent-456"
    assert run_in_db.agent_version == "2.0.0"
    assert run_in_db.environment_id == "env-789"
    assert run_in_db.trace_id == "trace-abc"
    assert run_in_db.benchmark_id == "bench-xyz"
    assert run_in_db.benchmark_version == "1.0.0"
    assert run_in_db.status == RunStatus.COMPLETED
    assert run_in_db.duration == 10.0
    assert run_in_db.configuration == {"key": "value"}
    assert run_in_db.metadata == {"test": "data"}
    assert isinstance(run_in_db.id, str)
    assert isinstance(run_in_db.created_at, datetime)
    assert isinstance(run_in_db.updated_at, datetime)


def test_evaluation_result_model():
    """Test the EvaluationResult model."""
    result = EvaluationResult(
        run_id="run-123",
        evaluator_id="eval-task-success",
        metric_name="task_success",
        score=1.0,
        passed=True,
        explanation="Task completed successfully",
        metadata={"details": "All criteria met"}
    )

    assert result.run_id == "run-123"
    assert result.evaluator_id == "eval-task-success"
    assert result.metric_name == "task_success"
    assert result.score == 1.0
    assert result.passed is True
    assert result.explanation == "Task completed successfully"
    assert result.metadata == {"details": "All criteria met"}
    assert isinstance(result.evaluation_id, str)
    assert isinstance(result.created_at, datetime)


def test_run_status_enum():
    """Test the RunStatus enum."""
    assert RunStatus.PENDING == "PENDING"
    assert RunStatus.RUNNING == "RUNNING"
    assert RunStatus.COMPLETED == "COMPLETED"
    assert RunStatus.FAILED == "FAILED"
    assert RunStatus.CANCELLED == "CANCELLED"

    # Test that we can iterate over the enum
    statuses = list(RunStatus)
    assert len(statuses) == 5
    assert RunStatus.PENDING in statuses
    assert RunStatus.RUNNING in statuses
    assert RunStatus.COMPLETED in statuses
    assert RunStatus.FAILED in statuses
    assert RunStatus.CANCELLED in statuses


def test_evaluation_run_status_validation():
    """Test that invalid status values are rejected."""
    with pytest.raises(ValidationError):
        EvaluationRun(
            task_id="task-123",
            task_version="1.0.0",
            agent_id="agent-456",
            agent_version="2.0.0",
            environment_id="env-789",
            status="INVALID_STATUS"  # Not a valid RunStatus
        )


def test_evaluation_run_required_fields():
    """Test that required fields are enforced."""
    # Missing task_id
    with pytest.raises(ValidationError):
        EvaluationRun(
            # task_id is missing
            task_version="1.0.0",
            agent_id="agent-456",
            agent_version="2.0.0",
            environment_id="env-789"
        )

    # Missing task_version
    with pytest.raises(ValidationError):
        EvaluationRun(
            task_id="task-123",
            # task_version is missing
            agent_id="agent-456",
            agent_version="2.0.0",
            environment_id="env-789"
        )

    # Missing agent_id
    with pytest.raises(ValidationError):
        EvaluationRun(
            task_id="task-123",
            task_version="1.0.0",
            # agent_id is missing
            agent_version="2.0.0",
            environment_id="env-789"
        )

    # Missing agent_version
    with pytest.raises(ValidationError):
        EvaluationRun(
            task_id="task-123",
            task_version="1.0.0",
            agent_id="agent-456",
            # agent_version is missing
            environment_id="env-789"
        )

    # Missing environment_id
    with pytest.raises(ValidationError):
        EvaluationRun(
            task_id="task-123",
            task_version="1.0.0",
            agent_id="agent-456",
            agent_version="2.0.0",
            # environment_id is missing
        )


def test_evaluation_run_serialization():
    """Test serialization to dict and JSON."""
    now = datetime.now(timezone.utc)
    run = EvaluationRun(
        task_id="task-123",
        task_version="1.0.0",
        agent_id="agent-456",
        agent_version="2.0.0",
        environment_id="env-789",
        trace_id="trace-abc",
        benchmark_id="bench-xyz",
        benchmark_version="1.0.0",
        status=RunStatus.COMPLETED,
        started_at=now - timedelta(seconds=5),
        completed_at=now,
        duration=5.0,
        configuration={"test": True},
        metadata={"key": "value"}
    )

    # Test dict serialization
    run_dict = run.model_dump()
    assert run_dict["task_id"] == "task-123"
    assert run_dict["task_version"] == "1.0.0"
    assert run_dict["agent_id"] == "agent-456"
    assert run_dict["agent_version"] == "2.0.0"
    assert run_dict["environment_id"] == "env-789"
    assert run_dict["trace_id"] == "trace-abc"
    assert run_dict["benchmark_id"] == "bench-xyz"
    assert run_dict["benchmark_version"] == "1.0.0"
    assert run_dict["status"] == RunStatus.COMPLETED
    assert run_dict["duration"] == 5.0
    assert run_dict["configuration"] == {"test": True}
    assert run_dict["metadata"] == {"key": "value"}
    assert run_dict["started_at"] == now - timedelta(seconds=5)
    assert run_dict["completed_at"] == now

    # Test JSON serialization
    run_json = run.model_dump_json()
    assert "task-123" in run_json
    assert "agent-456" in run_json
    assert "env-789" in run_json
    assert "trace-abc" in run_json
    assert "bench-xyz" in run_json
    assert "COMPLETED" in run_json


def test_evaluation_run_from_orm():
    """Test creating a domain model from an ORM object (simulated)."""
    # Simulate an ORM object (we'll use a simple class for this test)
    class FakeORM:
        def __init__(self):
            self.id = "fake-id"
            self.task_id = "task-123"
            self.task_version = "1.0.0"
            self.agent_id = "agent-456"
            self.agent_version = "2.0.0"
            self.environment_id = "env-789"
            self.trace_id = "trace-abc"
            self.benchmark_id = "bench-xyz"
            self.benchmark_version = "1.0.0"
            self.status = RunStatus.COMPLETED
            self.started_at = datetime.now(timezone.utc) - timedelta(seconds=10)
            self.completed_at = datetime.now(timezone.utc)
            self.duration = 10.0
            self.configuration = {"key": "value"}
            self.metadata_ = {"metadata": "data"}
            self.created_at = datetime.now(timezone.utc) - timedelta(seconds=20)
            self.updated_at = datetime.now(timezone.utc) - timedelta(seconds=10)

    fake_orm = FakeORM()
    # In a real implementation, we would have a mapper function.
    # For now, we just test that the domain model can be instantiated with the same data.
    run = EvaluationRun(
        id=fake_orm.id,
        task_id=fake_orm.task_id,
        task_version=fake_orm.task_version,
        agent_id=fake_orm.agent_id,
        agent_version=fake_orm.agent_version,
        environment_id=fake_orm.environment_id,
        trace_id=fake_orm.trace_id,
        benchmark_id=fake_orm.benchmark_id,
        benchmark_version=fake_orm.benchmark_version,
        status=fake_orm.status,
        started_at=fake_orm.started_at,
        completed_at=fake_orm.completed_at,
        duration=fake_orm.duration,
        configuration=fake_orm.configuration,
        metadata=fake_orm.metadata_,
        created_at=fake_orm.created_at,
        updated_at=fake_orm.updated_at
    )

    assert run.id == "fake-id"
    assert run.task_id == "task-123"
    assert run.status == RunStatus.COMPLETED
    assert run.configuration == {"key": "value"}


if __name__ == "__main__":
    pytest.main([__file__])