"""Evaluator interface and base classes."""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from uuid import UUID

from backend.app.domain.evaluations.models import EvaluationRun
from backend.app.domain.traces.models import Trace
from backend.app.domain.tasks.models import Task


@runtime_checkable
class Evaluator(Protocol):
    """Protocol defining the evaluator interface."""

    def evaluate(self, run: EvaluationRun, trace: Trace, task: Task) -> 'EvaluationResult':
        """Evaluate a trace against a task.

        Args:
            run: The evaluation run
            trace: The trace to evaluate
            task: The task being evaluated

        Returns:
            EvaluationResult containing the evaluation outcome
        """
        ...


class BaseEvaluator(ABC):
    """Abstract base class for evaluators."""

    @abstractmethod
    def evaluate(self, run: EvaluationRun, trace: Trace, task: Task) -> 'EvaluationResult':
        """Evaluate a trace against a task.

        Args:
            run: The evaluation run
            trace: The trace to evaluate
            task: The task being evaluated

        Returns:
            EvaluationResult containing the evaluation outcome
        """
        pass