"""Task success evaluator for determining if an agent completed a task successfully."""

from typing import Any
from uuid import UUID

from backend.app.domain.evaluations.evaluator import BaseEvaluator
from backend.app.domain.evaluations.models import EvaluationResult
from backend.app.domain.evaluations.models import EvaluationRun
from backend.app.domain.tasks.models import Task
from bcrypt import Trace


class TaskSuccessEvaluator(BaseEvaluator):
    """
    Deterministic evaluator that checks if the agent's final output matches the expected outcome.

    This evaluator compares the task's expected outcome with the actual execution result
    found in the trace. It looks for the final ACTION_COMPLETED or AGENT_COMPLETED event
    that contains the output, and compares it to the task's expected_outcome field.

    The comparison is done as string equality for simplicity in Phase 2.
    Future phases may implement more sophisticated comparison (semantic similarity, etc.).
    """

    def __init__(self, evaluator_id: str = "task_success_evaluator"):
        self.evaluator_id = evaluator_id

    def evaluate(self, run: EvaluationRun, trace: Trace, task: Task) -> EvaluationResult:
        """
        Evaluate whether the agent successfully completed the task.

        Args:
            run: The evaluation run
            trace: The trace containing the execution events
            task: The task being evaluated

        Returns:
            EvaluationResult with score 1.0 if successful, 0.0 if not
        """
        # Extract the final output from the trace
        actual_output = self._extract_final_output(trace)
        expected_outcome = task.expected_outcome

        # Handle case where no expected outcome is defined
        if expected_outcome is None:
            # If no expected outcome, we cannot determine success/failure
            # In this case, we consider it not applicable and return a neutral score
            return EvaluationResult(
                run_id=str(run.id),
                evaluator_id=self.evaluator_id,
                metric_name="task_success",
                score=0.5,  # Neutral score when no criteria defined
                passed=False,  # Not passed since we can't verify
                explanation="No expected outcome defined for task - cannot determine success",
                metadata={
                    "actual_output": actual_output,
                    "expected_outcome": None
                }
            )

        # Convert both to strings for comparison
        actual_str = str(actual_output) if actual_output is not None else ""
        expected_str = str(expected_outcome) if expected_outcome is not None else ""

        # Simple string equality comparison
        passed = actual_str == expected_str
        score = 1.0 if passed else 0.0

        explanation = (
            f"Task success evaluation: expected '{expected_str}', got '{actual_str}'"
        )

        return EvaluationResult(
            run_id=str(run.id),
            evaluator_id=self.evaluator_id,
            metric_name="task_success",
            score=score,
            passed=passed,
            explanation=explanation,
            metadata={
                "actual_output": actual_output,
                "expected_outcome": expected_outcome,
                "comparison_type": "string_equality"
            }
        )

    def _extract_final_output(self, trace: Trace) -> Any:
        """
        Extract the final output from a trace.

        Looks through trace events in chronological order to find the final
        meaningful output from ACTION_COMPLETED or AGENT_COMPLETED events.

        Args:
            trace: The trace to examine

        Returns:
            The final output value, or None if no output found
        """
        if not trace.events:
            return None

        # Look for the last ACTION_COMPLETED or AGENT_COMPLETED event with output
        final_output = None

        for event in trace.events:
            if event.event_type.value in ["ACTION_COMPLETED", "AGENT_COMPLETED"]:
                # Extract output from payload
                output = event.payload.get("output")
                if output is not None:
                    final_output = output

            # Also check TASK_COMPLETED events
            elif event.event_type.value == "TASK_COMPLETED":
                output = event.payload.get("output")
                if output is not None:
                    final_output = output

        return final_output