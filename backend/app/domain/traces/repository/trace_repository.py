"""Trace repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from backend.app.domain.traces.models import Trace
from backend.app.domain.traces.query import TraceQuery


class TraceRepository(ABC):
    """Abstract base class for trace repository."""

    @abstractmethod
    def save(self, trace: Trace) -> Trace:
        """Save a trace and return the saved entity."""
        raise NotImplementedError

    @abstractmethod
    def get(self, trace_id: UUID) -> Optional[Trace]:
        """Get a trace by ID."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, trace_id: UUID) -> bool:
        """Check if a trace exists."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, trace_id: UUID) -> bool:
        """Delete a trace by ID. Returns True if deleted, False if not found."""
        raise NotImplementedError

    @abstractmethod
    def get_by_run_id(self, run_id: UUID) -> List[Trace]:
        """Get traces by run ID."""
        raise NotImplementedError

    @abstractmethod
    def get_by_trace_id(self, trace_id: UUID) -> Optional[Trace]:
        """Get a trace by trace ID (alias for get for clarity)."""
        raise NotImplementedError

    @abstractmethod
    def query(self, query_params: TraceQuery) -> List[Trace]:
        """Query traces with filtering and pagination.

        Args:
            query_params: TraceQuery object containing filter criteria and pagination options

        Returns:
            List of traces matching the query criteria
        """
        raise NotImplementedError