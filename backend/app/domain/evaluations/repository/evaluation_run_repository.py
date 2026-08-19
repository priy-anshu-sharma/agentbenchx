"""Evaluation run repository interface."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from backend.app.domain.evaluations.models import EvaluationRun


class EvaluationRunRepository(ABC):
    """Abstract base class for evaluation run repository."""

    @abstractmethod
    def save(self, evaluation_run: EvaluationRun) -> EvaluationRun:
        """Save an evaluation run and return the saved entity."""
        raise NotImplementedError

    @abstractmethod
    def get(self, evaluation_run_id: UUID) -> Optional[EvaluationRun]:
        """Get an evaluation run by ID."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, evaluation_run_id: UUID) -> bool:
        """Check if an evaluation run exists."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, evaluation_run_id: UUID) -> bool:
        """Delete an evaluation run by ID. Returns True if deleted, False if not found."""
        raise NotImplementedError