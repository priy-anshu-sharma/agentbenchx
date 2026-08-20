"""Tests for the SQLAlchemy trace repository implementation."""

import pytest
import uuid
from datetime import datetime, timezone
from uuid import UUID, uuid4
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from backend.app.infrastructure.database.repository.trace_repository import SQLAlchemyTraceRepository
from backend.app.infrastructure.database.models.trace import Trace as SQLTrace
from backend.app.infrastructure.database.models.trace_event import TraceEvent as SQLTraceEvent
from backend.app.domain.traces.models import Trace, TraceEvent, TraceEventType
from backend.app.domain.traces.query import TraceQuery
from backend.app.infrastructure.database.base import Base


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
    def db_session(self):
        """Create a real database session for testing."""
        # Use SQLite in-memory database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

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
        assert trace_call_args[0][0].id == uuid.UUID(sample_trace.id)  # SQLAlchemy converts string ID to UUID object
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
        assert trace_call_args[0][0].id == uuid.UUID(sample_trace_with_events.id)  # SQLAlchemy converts string ID to UUID object

        # Verify events were added
        event_call_args = mock_session.add.call_args_list[1:]
        assert len(event_call_args) == 2
        for i, call_args in enumerate(event_call_args):
            event_arg = call_args[0][0]
            assert isinstance(event_arg, SQLTraceEvent)
            assert event_arg.trace_id == uuid.UUID(sample_trace_with_events.id)  # SQLAlchemy converts string ID to UUID object
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


    def test_query_traces_no_filters(self, repository, mock_session, sample_trace_with_events):
        """Test querying traces with no filters returns all traces."""
        # Setup mocks
        mock_db_trace = MagicMock()
        mock_db_trace.id = sample_trace_with_events.id
        mock_db_trace.agent_id = sample_trace_with_events.agent_id
        mock_db_trace.task_id = sample_trace_with_events.task_id
        mock_db_trace.environment_id = sample_trace_with_events.environment_id
        mock_db_trace.status = sample_trace_with_events.status
        mock_db_trace.run_id = sample_trace_with_events.run_id
        mock_db_trace.started_at = sample_trace_with_events.started_at
        mock_db_trace.ended_at = sample_trace_with_events.ended_at
        mock_db_trace.metadata_ = sample_trace_with_events.metadata

        # Mock events
        mock_db_event1 = MagicMock()
        mock_db_event1.id = uuid4()
        mock_db_event1.event_type = TraceEventType.TASK_STARTED.value
        mock_db_event1.sequence_number = 0
        mock_db_event1.timestamp = sample_trace_with_events.events[0].timestamp
        mock_db_event1.payload = sample_trace_with_events.events[0].payload
        mock_db_event1.metadata_ = sample_trace_with_events.events[0].metadata

        mock_db_event2 = MagicMock()
        mock_db_event2.id = uuid4()
        mock_db_event2.event_type = TraceEventType.AGENT_STARTED.value
        mock_db_event2.sequence_number = 1
        mock_db_event2.timestamp = sample_trace_with_events.events[1].timestamp
        mock_db_event2.payload = sample_trace_with_events.events[1].payload
        mock_db_event2.metadata_ = sample_trace_with_events.events[1].metadata

        # For no filters, we need to mock the trace query chain:
        # query().filter().order_by().offset().limit().all()
        mock_trace_query = MagicMock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query  # First filter call
        mock_trace_query.filter.return_value = mock_trace_query  # Second filter call (if any)
        mock_trace_query.filter.return_value = mock_trace_query  # Third filter call (if any)
        mock_trace_query.filter.return_value = mock_trace_query  # Fourth filter call (if any)
        mock_trace_query.order_by.return_value = mock_trace_query
        mock_trace_query.offset.return_value = mock_trace_query
        mock_trace_query.limit.return_value = mock_trace_query
        mock_trace_query.all.return_value = [mock_db_trace]

        # Mock the events query
        mock_events_query = MagicMock()
        mock_events_query.filter.return_value = mock_events_query
        mock_events_query.order_by.return_value = mock_events_query
        mock_events_query.all.return_value = [mock_db_event1, mock_db_event2]

        # We need to handle that session.query() is called twice - once for traces, once for events
        call_count = 0
        def query_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_trace_query
            else:
                return mock_events_query

        mock_session.query.side_effect = query_side_effect

        # Execute query with no filters
        query_params = TraceQuery()
        result = repository.query(query_params)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == sample_trace_with_events.id
        assert result[0].agent_id == sample_trace_with_events.agent_id
        assert len(result[0].events) == 2

    def test_query_traces_filter_by_run_id(self, repository, mock_session, sample_trace_with_events):
        """Test querying traces filtered by run ID."""
        # Setup mocks
        mock_db_trace = MagicMock()
        mock_db_trace.id = sample_trace_with_events.id
        mock_db_trace.agent_id = sample_trace_with_events.agent_id
        mock_db_trace.task_id = sample_trace_with_events.task_id
        mock_db_trace.environment_id = sample_trace_with_events.environment_id
        mock_db_trace.status = sample_trace_with_events.status
        mock_db_trace.run_id = sample_trace_with_events.run_id
        mock_db_trace.started_at = sample_trace_with_events.started_at
        mock_db_trace.ended_at = sample_trace_with_events.ended_at
        mock_db_trace.metadata_ = sample_trace_with_events.metadata

        # Mock events
        mock_db_event1 = MagicMock()
        mock_db_event1.id = uuid4()
        mock_db_event1.event_type = TraceEventType.TASK_STARTED.value
        mock_db_event1.sequence_number = 0
        mock_db_event1.timestamp = sample_trace_with_events.events[0].timestamp
        mock_db_event1.payload = sample_trace_with_events.events[0].payload
        mock_db_event1.metadata_ = sample_trace_with_events.events[0].metadata

        mock_db_event2 = MagicMock()
        mock_db_event2.id = uuid4()
        mock_db_event2.event_type = TraceEventType.AGENT_STARTED.value
        mock_db_event2.sequence_number = 1
        mock_db_event2.timestamp = sample_trace_with_events.events[1].timestamp
        mock_db_event2.payload = sample_trace_with_events.events[1].payload
        mock_db_event2.metadata_ = sample_trace_with_events.events[1].metadata

        # Set up proper mock chain for the trace query
        # session.query(SQLTrace) -> query object
        mock_trace_query = MagicMock()
        mock_session.query.return_value = mock_trace_query

        # Apply filters (each filter returns the same query object for chaining)
        mock_trace_query.filter.return_value = mock_trace_query

        # Apply ordering
        mock_trace_query.order_by.return_value = mock_trace_query

        # Apply pagination
        mock_trace_query.offset.return_value = mock_trace_query
        mock_trace_query.limit.return_value = mock_trace_query

        # Execute query
        mock_trace_query.all.return_value = [mock_db_trace]

        # Set up proper mock chain for the events query (separate call)
        mock_events_query = MagicMock()
        # We need to differentiate between the two session.query() calls
        call_count = 0
        def query_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call is for traces
                return mock_trace_query
            else:
                # Second call is for events
                mock_events_query.filter.return_value = mock_events_query
                mock_events_query.order_by.return_value = mock_events_query
                mock_events_query.all.return_value = [mock_db_event1, mock_db_event2]
                return mock_events_query

        mock_session.query.side_effect = query_side_effect

        # Execute query with run_id filter
        query_params = TraceQuery(run_id=sample_trace_with_events.run_id)
        result = repository.query(query_params)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == sample_trace_with_events.id
        assert result[0].run_id == sample_trace_with_events.run_id

    def test_query_traces_filter_by_agent_id(self, repository, mock_session, sample_trace_with_events):
        """Test querying traces filtered by agent ID."""
        # Setup mocks
        mock_db_trace = MagicMock()
        mock_db_trace.id = sample_trace_with_events.id
        mock_db_trace.agent_id = sample_trace_with_events.agent_id
        mock_db_trace.task_id = sample_trace_with_events.task_id
        mock_db_trace.environment_id = sample_trace_with_events.environment_id
        mock_db_trace.status = sample_trace_with_events.status
        mock_db_trace.run_id = sample_trace_with_events.run_id
        mock_db_trace.started_at = sample_trace_with_events.started_at
        mock_db_trace.ended_at = sample_trace_with_events.ended_at
        mock_db_trace.metadata_ = sample_trace_with_events.metadata

        # Mock events
        mock_db_event1 = MagicMock()
        mock_db_event1.id = uuid4()
        mock_db_event1.event_type = TraceEventType.TASK_STARTED.value
        mock_db_event1.sequence_number = 0
        mock_db_event1.timestamp = sample_trace_with_events.events[0].timestamp
        mock_db_event1.payload = sample_trace_with_events.events[0].payload
        mock_db_event1.metadata_ = sample_trace_with_events.events[0].metadata

        # Set up proper mock chain for the trace query
        mock_trace_query = MagicMock()
        mock_session.query.return_value = mock_trace_query

        # Apply filters (each filter returns the same query object for chaining)
        mock_trace_query.filter.return_value = mock_trace_query

        # Apply ordering
        mock_trace_query.order_by.return_value = mock_trace_query

        # Apply pagination
        mock_trace_query.offset.return_value = mock_trace_query
        mock_trace_query.limit.return_value = mock_trace_query

        # Execute query
        mock_trace_query.all.return_value = [mock_db_trace]

        # Set up proper mock chain for the events query (separate call)
        mock_events_query = MagicMock()
        # We need to differentiate between the two session.query() calls
        call_count = 0
        def query_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call is for traces
                return mock_trace_query
            else:
                # Second call is for events
                mock_events_query.filter.return_value = mock_events_query
                mock_events_query.order_by.return_value = mock_events_query
                mock_events_query.all.return_value = [mock_db_event1]
                return mock_events_query

        mock_session.query.side_effect = query_side_effect

        # Execute query with agent_id filter
        query_params = TraceQuery(agent_id=sample_trace_with_events.agent_id)
        result = repository.query(query_params)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == sample_trace_with_events.id
        assert result[0].agent_id == sample_trace_with_events.agent_id

    def test_query_traces_filter_by_event_type_real_db(self, db_session):
        """Test querying traces filtered by event type using real database."""
        repository = SQLAlchemyTraceRepository(db_session)

        # Create multiple traces with different event types
        trace1_id = uuid4()
        trace1_run_id = uuid4()
        trace1 = Trace(
            id=str(trace1_id),
            agent_id="agent-123",
            task_id="task-456",
            environment_id="env-789",
            status="SUCCESS",
            run_id=str(trace1_run_id),
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            metadata={"test": "data1"}
        )

        trace2_id = uuid4()
        trace2_run_id = uuid4()
        trace2 = Trace(
            id=str(trace2_id),
            agent_id="agent-456",
            task_id="task-789",
            environment_id="env-999",
            status="SUCCESS",
            run_id=str(trace2_run_id),
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            metadata={"test": "data2"}
        )

        # Add events to trace1 - TASK_STARTED and AGENT_STARTED
        event1_1 = TraceEvent(
            event_type=TraceEventType.TASK_STARTED,
            timestamp=1234567890.0,
            sequence_number=0,
            payload={"task_id": "task-456"},
            metadata={"source": "test"}
        )
        event1_2 = TraceEvent(
            event_type=TraceEventType.AGENT_STARTED,
            timestamp=1234567891.0,
            sequence_number=1,
            payload={"agent_id": "agent-123"},
            metadata={"version": "1.0"}
        )
        trace1.add_event(event1_1)
        trace1.add_event(event1_2)

        # Add events to trace2 - TOOL_EXECUTED and ACTION_COMPLETED
        event2_1 = TraceEvent(
            event_type=TraceEventType.TOOL_EXECUTED,
            timestamp=1234567892.0,
            sequence_number=0,
            payload={"action_id": "action-123", "tool_name": "test-tool"},
            metadata={"source": "test"}
        )
        event2_2 = TraceEvent(
            event_type=TraceEventType.ACTION_COMPLETED,
            timestamp=1234567893.0,
            sequence_number=1,
            payload={"action_id": "action-123", "success": True},
            metadata={"source": "test"}
        )
        trace2.add_event(event2_1)
        trace2.add_event(event2_2)

        # Save both traces
        repository.save(trace1)
        repository.save(trace2)

        # Query for TASK_STARTED events - should return trace1 only
        query_params = TraceQuery(event_type=TraceEventType.TASK_STARTED)
        result = repository.query(query_params)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == trace1.id
        assert len(result[0].events) == 2  # Both events should be returned for the trace
        # Events should be in correct order
        assert result[0].events[0].event_type == TraceEventType.TASK_STARTED
        assert result[0].events[1].event_type == TraceEventType.AGENT_STARTED

        # Query for ACTION_COMPLETED events - should return trace2 only
        query_params = TraceQuery(event_type=TraceEventType.ACTION_COMPLETED)
        result = repository.query(query_params)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == trace2.id
        assert len(result[0].events) == 2  # Both events should be returned for the trace
        # Events should be in correct order
        assert result[0].events[0].event_type == TraceEventType.TOOL_EXECUTED
        assert result[0].events[1].event_type == TraceEventType.ACTION_COMPLETED

        # Query for non-existent event type - should return empty
        query_params = TraceQuery(event_type=TraceEventType.ERROR)
        result = repository.query(query_params)

        # Verify
        assert len(result) == 0

    def test_query_traces_pagination(self, repository, mock_session):
        """Test querying traces with pagination."""
        # Create multiple sample traces
        traces = []
        for i in range(5):
            trace_id = uuid4()
            run_id = uuid4()
            trace = Trace(
                id=str(trace_id),
                agent_id=f"agent-{i}",
                task_id=f"task-{i}",
                environment_id=f"env-{i}",
                status="SUCCESS",
                run_id=str(run_id),
                started_at=datetime(2026, 8, 19, 10, i, 0, tzinfo=timezone.utc),
                ended_at=datetime(2026, 8, 19, 10, i, 30, tzinfo=timezone.utc),
                metadata={"test": f"data-{i}"}
            )
            # Add one event to each trace
            event = TraceEvent(
                event_type=TraceEventType.TASK_STARTED,
                timestamp=1234567890.0 + i,
                sequence_number=0,
                payload={"task_id": f"task-{i}"},
                metadata={"source": "test"}
            )
            trace.add_event(event)
            traces.append(trace)

        # Setup mocks for multiple traces
        mock_db_traces = []
        for trace in traces:
            mock_db_trace = MagicMock()
            mock_db_trace.id = trace.id
            mock_db_trace.agent_id = trace.agent_id
            mock_db_trace.task_id = trace.task_id
            mock_db_trace.environment_id = trace.environment_id
            mock_db_trace.status = trace.status
            mock_db_trace.run_id = trace.run_id
            mock_db_trace.started_at = trace.started_at
            mock_db_trace.ended_at = trace.ended_at
            mock_db_trace.metadata_ = trace.metadata
            mock_db_traces.append(mock_db_trace)

        # Mock events for each trace
        mock_db_events = []
        for i, trace in enumerate(traces):
            mock_db_event = MagicMock()
            mock_db_event.id = uuid4()
            mock_db_event.event_type = TraceEventType.TASK_STARTED.value  # Ensure it's a string
            mock_db_event.sequence_number = 0
            mock_db_event.timestamp = trace.events[0].timestamp
            mock_db_event.payload = trace.events[0].payload
            mock_db_event.metadata_ = trace.events[0].metadata
            mock_db_events.append(mock_db_event)

        # For pagination test, we need:
        # 1. First call to session.query() returns trace query object
        # 2. Second call to session.query() returns events query object

        # Set up trace query mock
        mock_trace_query = MagicMock()
        # Configure the trace query to return our paginated traces when all() is called
        mock_trace_query.all.return_value = [mock_db_traces[2], mock_db_traces[3]]  # Page 1: traces 2 and 3 (limit=2, offset=2)

        # Set up the filter/order_by/offset/limit chaining for trace query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.order_by.return_value = mock_trace_query
        mock_trace_query.offset.return_value = mock_trace_query
        mock_trace_query.limit.return_value = mock_trace_query

        # Set up events query mock
        mock_events_query = MagicMock()
        # Configure the events query to return events when all() is called
        # We'll configure this based on which trace's events are being requested
        call_count_for_events = [0]  # Use list to allow modification in nested function

        def events_query_all():
            call_count_for_events[0] += 1
            if call_count_for_events[0] == 1:
                return [mock_db_events[2]]  # Events for trace 2
            elif call_count_for_events[0] == 2:
                return [mock_db_events[3]]  # Events for trace 3
            else:
                return []

        mock_events_query.all.side_effect = events_query_all
        mock_events_query.filter.return_value = mock_events_query
        mock_events_query.order_by.return_value = mock_events_query

        # Set up the session.query side effect to return appropriate query objects
        call_count = [0]  # Use list to allow modification in nested function
        def query_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call is for traces
                return mock_trace_query
            else:
                # Second call is for events
                return mock_events_query

        mock_session.query.side_effect = query_side_effect

        # Execute query with pagination
        query_params = TraceQuery(limit=2, offset=2)
        result = repository.query(query_params)

        # Verify
        assert len(result) == 2
        assert isinstance(result[0], Trace)
        assert isinstance(result[1], Trace)
        assert result[0].id == traces[2].id
        assert result[1].id == traces[3].id

    def test_query_traces_time_range_filter(self, repository, mock_session, sample_trace_with_events):
        """Test querying traces with time range filters."""
        # Setup mocks
        mock_db_trace = MagicMock()
        mock_db_trace.id = sample_trace_with_events.id
        mock_db_trace.agent_id = sample_trace_with_events.agent_id
        mock_db_trace.task_id = sample_trace_with_events.task_id
        mock_db_trace.environment_id = sample_trace_with_events.environment_id
        mock_db_trace.status = sample_trace_with_events.status
        mock_db_trace.run_id = sample_trace_with_events.run_id
        mock_db_trace.started_at = sample_trace_with_events.started_at
        mock_db_trace.ended_at = sample_trace_with_events.ended_at
        mock_db_trace.metadata_ = sample_trace_with_events.metadata

        # Mock events
        mock_db_event1 = MagicMock()
        mock_db_event1.id = uuid4()
        mock_db_event1.event_type = TraceEventType.TASK_STARTED.value
        mock_db_event1.sequence_number = 0
        mock_db_event1.timestamp = sample_trace_with_events.events[0].timestamp
        mock_db_event1.payload = sample_trace_with_events.events[0].payload
        mock_db_event1.metadata_ = sample_trace_with_events.events[0].metadata

        # Set up proper mock chain for the trace query
        mock_trace_query = MagicMock()
        mock_session.query.return_value = mock_trace_query

        # Apply filters (each filter returns the same query object for chaining)
        mock_trace_query.filter.return_value = mock_trace_query

        # Apply ordering
        mock_trace_query.order_by.return_value = mock_trace_query

        # Apply pagination
        mock_trace_query.offset.return_value = mock_trace_query
        mock_trace_query.limit.return_value = mock_trace_query

        # Execute query
        mock_trace_query.all.return_value = [mock_db_trace]

        # Set up proper mock chain for the events query (separate call)
        mock_events_query = MagicMock()
        # We need to differentiate between the two session.query() calls
        call_count = 0
        def query_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call is for traces
                return mock_trace_query
            else:
                # Second call is for events
                mock_events_query.filter.return_value = mock_events_query
                mock_events_query.order_by.return_value = mock_events_query
                mock_events_query.all.return_value = [mock_db_event1]
                return mock_events_query

        mock_session.query.side_effect = query_side_effect

        # Execute query with time range filters
        start_time = sample_trace_with_events.started_at
        end_time = sample_trace_with_events.ended_at or datetime.now(timezone.utc)
        query_params = TraceQuery(
            created_after=start_time,
            created_before=end_time
        )
        result = repository.query(query_params)

        # Verify
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == sample_trace_with_events.id

    def test_query_traces_invalid_time_range(self, repository):
        """Test that invalid time range (after > before) raises validation error."""
        # Execute and verify
        with pytest.raises(ValueError, match="created_after must be before created_before"):
            TraceQuery(
                created_after=datetime(2026, 8, 20, tzinfo=timezone.utc),
                created_before=datetime(2026, 8, 19, tzinfo=timezone.utc)
            )

    def test_query_traces_validation_limit_zero(self, repository):
        """Test that limit of zero raises validation error."""
        # Execute and verify
        with pytest.raises(ValueError):
            TraceQuery(limit=0)

    def test_query_traces_validation_negative_offset(self, repository):
        """Test that negative offset raises validation error."""
        # Execute and verify
        with pytest.raises(ValueError):
            TraceQuery(offset=-1)

    def test_query_traces_combined_filters_run_id_and_event_type(self, db_session):
        """Test querying traces with combined run_id and event_type filters."""
        repository = SQLAlchemyTraceRepository(db_session)

        # Create two traces with different run IDs
        trace1_id = uuid4()
        trace1_run_id = uuid4()
        trace1 = Trace(
            id=str(trace1_id),
            agent_id="agent-123",
            task_id="task-456",
            environment_id="env-789",
            status="SUCCESS",
            run_id=str(trace1_run_id),
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            metadata={"test": "data1"}
        )

        trace2_id = uuid4()
        trace2_run_id = uuid4()
        trace2 = Trace(
            id=str(trace2_id),
            agent_id="agent-456",
            task_id="task-789",
            environment_id="env-999",
            status="SUCCESS",
            run_id=str(trace2_run_id),
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            metadata={"test": "data2"}
        )

        # Add events to trace1 - TASK_STARTED and AGENT_STARTED
        event1_1 = TraceEvent(
            event_type=TraceEventType.TASK_STARTED,
            timestamp=1234567890.0,
            sequence_number=0,
            payload={"task_id": "task-456"},
            metadata={"source": "test"}
        )
        event1_2 = TraceEvent(
            event_type=TraceEventType.AGENT_STARTED,
            timestamp=1234567891.0,
            sequence_number=1,
            payload={"agent_id": "agent-123"},
            metadata={"version": "1.0"}
        )
        trace1.add_event(event1_1)
        trace1.add_event(event1_2)

        # Add events to trace2 - TASK_STARTED and TOOL_EXECUTED (different event type)
        event2_1 = TraceEvent(
            event_type=TraceEventType.TASK_STARTED,
            timestamp=1234567892.0,
            sequence_number=0,
            payload={"task_id": "task-789"},
            metadata={"source": "test"}
        )
        event2_2 = TraceEvent(
            event_type=TraceEventType.TOOL_EXECUTED,
            timestamp=1234567893.0,
            sequence_number=1,
            payload={"action_id": "action-123", "tool_name": "test-tool"},
            metadata={"source": "test"}
        )
        trace2.add_event(event2_1)
        trace2.add_event(event2_2)

        # Save both traces
        repository.save(trace1)
        repository.save(trace2)

        # Query for trace1's run_id with TASK_STARTED event type - should return trace1
        query_params = TraceQuery(run_id=trace1_run_id, event_type=TraceEventType.TASK_STARTED)
        result = repository.query(query_params)

        # Verify - should return only trace1
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == trace1.id
        assert result[0].run_id == str(trace1_run_id)
        # Should have both events since we're returning the full trace
        assert len(result[0].events) == 2
        assert result[0].events[0].event_type == TraceEventType.TASK_STARTED
        assert result[0].events[1].event_type == TraceEventType.AGENT_STARTED

        # Query for trace2's run_id with TOOL_EXECUTED event type - should return trace2
        query_params = TraceQuery(run_id=trace2_run_id, event_type=TraceEventType.TOOL_EXECUTED)
        result = repository.query(query_params)

        # Verify - should return only trace2
        assert len(result) == 1
        assert isinstance(result[0], Trace)
        assert result[0].id == trace2.id
        assert result[0].run_id == str(trace2_run_id)
        # Should have both events since we're returning the full trace
        assert len(result[0].events) == 2
        assert result[0].events[0].event_type == TraceEventType.TASK_STARTED
        assert result[0].events[1].event_type == TraceEventType.TOOL_EXECUTED

        # Query for trace1's run_id with TOOL_EXECUTED event type - should return empty (no match)
        query_params = TraceQuery(run_id=trace1_run_id, event_type=TraceEventType.TOOL_EXECUTED)
        result = repository.query(query_params)

        # Verify - should return empty
        assert len(result) == 0

        # Query for non-existent run_id with any event type - should return empty
        fake_run_id = uuid4()
        query_params = TraceQuery(run_id=fake_run_id, event_type=TraceEventType.TASK_STARTED)
        result = repository.query(query_params)

        # Verify - should return empty
        assert len(result) == 0