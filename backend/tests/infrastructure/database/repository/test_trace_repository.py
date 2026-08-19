"""Tests for the SQLAlchemy trace repository implementation."""

import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.infrastructure.database.repository.trace_repository import SQLAlchemyTraceRepository
from backend.app.infrastructure.database.models.trace import Trace as SQLTrace
from backend.app.infrastructure.database.models.trace_event import TraceEvent as SQLTraceEvent
from backend.app.domain.traces.models import Trace, TraceEvent, TraceEventType


class TestSQLAlchemyTraceRepository:
    """Test suite for SQLAlchemyTraceRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock SQLAlchemy session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def repository(self, mock_session):
        """Create a repository instance with mock session."""
        return SQLAlchemyTraceRepository(mock_session)

    @pytest.fixture
    def sample_trace(self):
        """Create a sample trace for testing."""
        trace_id = uuid4()
        run_id = uuid4()
        return Trace(
            id=str(trace_id),
            agent_id="agent-123",
            task_id="task-456",
            environment_id="env-789",
            status="SUCCESS",
            run_id=str(run_id),
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            metadata={"test": "data"}
        )

    @pytest.fixture
    def sample_trace_with_events(self):
        """Create a sample trace with events for testing."""
        trace_id = uuid4()
        run_id = uuid4()
        trace = Trace(
            id=str(trace_id),
            agent_id="agent-123",
            task_id="task-456",
            environment_id="env-789",
            status="SUCCESS",
            run_id=str(run_id),
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            metadata={"test": "data"}
        )

        # Add some events
        event1 = TraceEvent(
            event_type=TraceEventType.TASK_STARTED,
            timestamp=1234567890.0,
            sequence_number=0,
            payload={"task_id": "task-456"},
            metadata={"source": "test"}
        )
        event2 = TraceEvent(
            event_type=TraceEventType.AGENT_STARTED,
            timestamp=1234567891.0,
            sequence_number=1,
            payload={"agent_id": "agent-123"},
            metadata={"version": "1.0"}
        )
        trace.add_event(event1)
        trace.add_event(event2)

        return trace

    def test_save_empty_trace(self, repository, mock_session, sample_trace):
        """Test saving a trace with no events."""
        # Setup mocks
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Execute
        result = repository.save(sample_trace)

        # Verify
        assert result == sample_trace
        assert mock_session.add.call_count >= 1  # At least for the trace
        assert mock_session.commit.call_count == 1  # Once for the entire transaction
        assert mock_session.refresh.call_count >= 1

        # Verify trace was added
        trace_call_args = mock_session.add.call_args_list[0]
        assert isinstance(trace_call_args[0][0], SQLTrace)
        assert trace_call_args[0][0].id == sample_trace.id  # Both are strings
        assert trace_call_args[0][0].agent_id == sample_trace.agent_id
        assert trace_call_args[0][0].task_id == sample_trace.task_id

    def test_save_trace_with_events(self, repository, mock_session, sample_trace_with_events):
        """Test saving a trace with events."""
        # Setup mocks
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()

        # Execute
        result = repository.save(sample_trace_with_events)

        # Verify
        assert result == sample_trace_with_events
        # Should add trace + 2 events
        assert mock_session.add.call_count == 3
        assert mock_session.commit.call_count == 1  # Once for the entire transaction
        assert mock_session.refresh.call_count >= 1

        # Verify trace was added first
        trace_call_args = mock_session.add.call_args_list[0]
        assert isinstance(trace_call_args[0][0], SQLTrace)
        assert trace_call_args[0][0].id == sample_trace_with_events.id  # Both are strings

        # Verify events were added
        event_call_args = mock_session.add.call_args_list[1:]
        assert len(event_call_args) == 2
        for i, call_args in enumerate(event_call_args):
            event_arg = call_args[0][0]
            assert isinstance(event_arg, SQLTraceEvent)
            assert event_arg.trace_id == sample_trace_with_events.id  # Both are strings
            assert event_arg.sequence_number == i

    def get_trace_by_id_success(self, repository, mock_session, sample_trace):
        """Test getting a trace by ID when it exists."""
        # Setup mocks
        trace_id = UUID(sample_trace.id)

        # Mock the trace query result
        mock_db_trace = MagicMock()
        mock_db_trace.id = trace_id
        mock_db_trace.agent_id = sample_trace.agent_id
        mock_db_trace.task_id = sample_trace.task_id
        mock_db_trace.environment_id = sample_trace.environment_id
        mock_db_trace.status = sample_trace.status
        mock_db_trace.run_id = UUID(sample_trace.run_id)
        mock_db_trace.started_at = sample_trace.started_at
        mock_db_trace.ended_at = sample_trace.ended_at
        mock_db_trace.metadata_ = sample_trace.metadata

        # Mock the events query result
        mock_db_event1 = MagicMock()
        mock_db_event1.id = uuid4()
        mock_db_event1.event_type = TraceEventType.TASK_STARTED.value
        mock_db_event1.sequence_number = 0
        mock_db_event1.timestamp = 1234567890.0
        mock_db_event1.payload = {"task_id": "task-456"}
        mock_db_event1.metadata_ = {"source": "test"}

        mock_db_event2 = MagicMock()
        mock_db_event2.id = uuid4()
        mock_db_event2.event_type = TraceEventType.AGENT_STARTED.value
        mock_db_event2.sequence_number = 1
        mock_db_event2.timestamp = 1234567891.0
        mock_db_event2.payload = {"agent_id": "agent-123"}
        mock_db_event2.metadata_ = {"version": "1.0"}

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_db_trace,  # First call for trace query
            mock_db_event1, # Second call for events query first
            mock_db_event2  # Third call for events query second
        ]
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_db_event1,
            mock_db_event2
        ]

        # Execute
        result = repository.get(trace_id)

        # Verify
        assert result is not None
        assert isinstance(result, Trace)
        assert result.id == sample_trace.id
        assert result.agent_id == sample_trace.agent_id
        assert result.task_id == sample_trace.task_id
        assert result.environment_id == sample_trace.environment_id
        assert result.status == sample_trace.status
        assert result.run_id == sample_trace.run_id
        assert len(result.events) == 2
        assert result.events[0].event_type == TraceEventType.TASK_STARTED
        assert result.events[1].event_type == TraceEventType.AGENT_STARTED

    def test_get_trace_by_id_not_found(self, repository, mock_session):
        """Test getting a trace by ID when it doesn't exist."""
        # Setup mocks
        trace_id = uuid4()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Execute
        result = repository.get(trace_id)

        # Verify
        assert result is None

    def test_exists_true(self, repository, mock_session):
        """Test exists returns True when trace exists."""
        # Setup mocks
        trace_id = uuid4()
        mock_session.query.return_value.filter.return_value.count.return_value = 1

        # Execute
        result = repository.exists(trace_id)

        # Verify
        assert result is True

    def test_exists_false(self, repository, mock_session):
        """Test exists returns False when trace doesn't exist."""
        # Setup mocks
        trace_id = uuid4()
        mock_session.query.return_value.filter.return_value.count.return_value = 0

        # Execute
        result = repository.exists(trace_id)

        # Verify
        assert result is False

    def test_delete_success(self, repository, mock_session):
        """Test deleting a trace that exists."""
        # Setup mocks
        trace_id = uuid4()
        mock_db_trace = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_trace

        # Execute
        result = repository.delete(trace_id)

        # Verify
        assert result is True
        # Should delete events first, then trace
        assert mock_session.query.return_value.filter.return_value.delete.call_count == 1
        assert mock_session.delete.call_count == 1
        assert mock_session.commit.call_count == 1

    def test_delete_not_found(self, repository, mock_session):
        """Test deleting a trace that doesn't exist."""
        # Setup mocks
        trace_id = uuid4()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Execute
        result = repository.delete(trace_id)

        # Verify
        assert result is False
        # Should not attempt to delete anything
        assert mock_session.query.return_value.filter.return_value.delete.call_count == 0
        assert mock_session.delete.call_count == 0
        assert mock_session.commit.call_count == 0

    def test_get_by_run_id_success(self, repository, mock_session, sample_trace):
        """Test getting traces by run ID when trace exists."""
        # Setup mocks
        run_id = UUID(sample_trace.run_id)

        # Mock the trace query result
        mock_db_trace = MagicMock()
        mock_db_trace.id = UUID(sample_trace.id)
        mock_db_trace.agent_id = sample_trace.agent_id
        mock_db_trace.task_id = sample_trace.task_id
        mock_db_trace.environment_id = sample_trace.environment_id
        mock_db_trace.status = sample_trace.status
        mock_db_trace.run_id = run_id
        mock_db_trace.started_at = sample_trace.started_at
        mock_db_trace.ended_at = sample_trace.ended_at
        mock_db_trace.metadata_ = sample_trace.metadata

        # Mock the events query result
        mock_db_event1 = MagicMock()
        mock_db_event1.id = uuid4()
        mock_db_event1.event_type = TraceEventType.TASK_STARTED.value
        mock_db_event1.sequence_number = 0
        mock_db_event1.timestamp = 1234567890.0
        mock_db_event1.payload = {"task_id": "task-456"}
        mock_db_event1.metadata_ = {"source": "test"}

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_db_trace  # For trace query
        ]
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_db_event1
        ]

        # Execute
        result = repository.get_by_run_id(run_id)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == sample_trace.id
        assert result[0].run_id == sample_trace.run_id
        assert len(result[0].events) == 1
        assert result[0].events[0].event_type == TraceEventType.TASK_STARTED

    def test_get_by_run_id_not_found(self, repository, mock_session):
        """Test getting traces by run ID when no trace exists."""
        # Setup mocks
        run_id = uuid4()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Execute
        result = repository.get_by_run_id(run_id)

        # Verify
        assert result == []

    def test_get_by_trace_id_alias(self, repository, mock_session):
        """Test that get_by_trace_id is an alias for get."""
        # Setup mocks
        trace_id = uuid4()
        mock_trace = MagicMock()
        # Set up the mock trace with proper attribute values
        mock_trace.id = trace_id
        mock_trace.agent_id = "agent-123"
        mock_trace.task_id = "task-456"
        mock_trace.environment_id = "env-789"
        mock_trace.status = "SUCCESS"
        mock_trace.run_id = uuid4()
        mock_trace.started_at = datetime.now(timezone.utc)
        mock_trace.ended_at = datetime.now(timezone.utc)
        mock_trace.metadata_ = {"test": "data"}

        mock_session.query.return_value.filter.return_value.first.return_value = mock_trace
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        # Execute
        result1 = repository.get(trace_id)
        result2 = repository.get_by_trace_id(trace_id)

        # Verify
        assert result1 == result2
        assert mock_session.query.return_value.filter.return_value.first.call_count == 2

    def test_save_trace_events_failure_rollback(self, repository, mock_session, sample_trace_with_events):
        """Test that failure to save events rolls back the entire transaction."""
        # Setup mocks
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock(side_effect=Exception("Database failure on event save"))
        mock_session.rollback = MagicMock()
        mock_session.refresh = MagicMock()

        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Database failure on event save"):
            repository.save(sample_trace_with_events)

        # Verify rollback was called
        mock_session.rollback.assert_called_once()

        # Verify commit WAS called (but failed, triggering rollback)
        mock_session.commit.assert_called_once()

        # Verify add was called for trace and events (before the failure)
        # Should add trace + 2 events
        assert mock_session.add.call_count == 3

    def test_save_trace_events_integrity_failure_rollback(self, repository, mock_session, sample_trace_with_events):
        """Test that integrity failure during event save rolls back the entire transaction."""
        # Setup mocks to simulate an integrity error on the second event
        mock_session.add = MagicMock(side_effect=[
            None,  # First add (trace) succeeds
            None,  # Second add (first event) succeeds
            IntegrityError("StatementError", "params", Exception("Integrity constraint violation"))  # Third add (second event) fails
        ])
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()
        mock_session.refresh = MagicMock()

        # Execute and verify integrity error is raised
        with pytest.raises(IntegrityError):
            repository.save(sample_trace_with_events)

        # Verify rollback was called
        mock_session.rollback.assert_called_once()

        # Verify commit was NOT called (due to rollback)
        mock_session.commit.assert_not_called()