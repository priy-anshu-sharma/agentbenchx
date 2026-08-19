"""SQLAlchemy implementation of evaluation run repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.domain.evaluations.models import EvaluationRun
from backend.app.domain.evaluations.repository.evaluation_run_repository import EvaluationRunRepository as AbstractEvaluationRunRepository
from backend.app.infrastructure.database.models.evaluation_run import EvaluationRun as SQLEvaluationRun, RunStatus


class SQLAlchemyEvaluationRunRepository(AbstractEvaluationRunRepository):
    """SQLAlchemy implementation of evaluation run repository."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, evaluation_run: EvaluationRun) -> EvaluationRun:
        """Save an evaluation run and return the saved entity."""
        # Convert domain model to SQLAlchemy model
        db_evaluation_run = SQLEvaluationRun(
            id=evaluation_run.id,
            task_id=evaluation_run.task_id,
            task_version=evaluation_run.task_version,
            agent_id=evaluation_run.agent_id,
            agent_version=evaluation_run.agent_version,
            environment_id=evaluation_run.environment_id,
            trace_id=evaluation_run.trace_id,
            benchmark_id=evaluation_run.benchmark_id,
            benchmark_version=evaluation_run.benchmark_version,
            status=evaluation_run.status,
            started_at=evaluation_run.started_at,
            completed_at=evaluation_run.completed_at,
            duration=evaluation_run.duration,
            configuration=evaluation_run.configuration,
            metadata_=evaluation_run.metadata,
        )

        self.session.add(db_evaluation_run)
        self.session.commit()
        self.session.refresh(db_evaluation_run)

        # Convert back to domain model
        return EvaluationRun(
            id=db_evaluation_run.id,
            task_id=db_evaluation_run.task_id,
            task_version=db_evaluation_run.task_version,
            agent_id=db_evaluation_run.agent_id,
            agent_version=db_evaluation_run.agent_version,
            environment_id=db_evaluation_run.environment_id,
            trace_id=db_evaluation_run.trace_id,
            benchmark_id=db_evaluation_run.benchmark_id,
            benchmark_version=db_evaluation_run.benchmark_version,
            status=db_evaluation_run.status,
            started_at=db_evaluation_run.started_at,
            completed_at=db_evaluation_run.completed_at,
            duration=db_evaluation_run.duration,
            configuration=db_evaluation_run.configuration,
            metadata=db_evaluation_run.metadata_,
            created_at=db_evaluation_run.created_at,
            updated_at=db_evaluation_run.updated_at,
        )

    def get(self, evaluation_run_id: UUID) -> Optional[EvaluationRun]:
        """Get an evaluation run by ID."""
        db_evaluation_run = self.session.query(SQLEvaluationRun).filter(
            SQLEvaluationRun.id == evaluation_run_id
        ).first()

        if not db_evaluation_run:
            return None

        return EvaluationRun(
            id=db_evaluation_run.id,
            task_id=db_evaluation_run.task_id,
            task_version=db_evaluation_run.task_version,
            agent_id=db_evaluation_run.agent_id,
            agent_version=db_evaluation_run.agent_version,
            environment_id=db_evaluation_run.environment_id,
            trace_id=db_evaluation_run.trace_id,
            benchmark_id=db_evaluation_run.benchmark_id,
            benchmark_version=db_evaluation_run.benchmark_version,
            status=db_evaluation_run.status,
            started_at=db_evaluation_run.started_at,
            completed_at=db_evaluation_run.completed_at,
            duration=db_evaluation_run.duration,
            configuration=db_evaluation_run.configuration,
            metadata=db_evaluation_run.metadata_,
            created_at=db_evaluation_run.created_at,
            updated_at=db_evaluation_run.updated_at,
        )

    def exists(self, evaluation_run_id: UUID) -> bool:
        """Check if an evaluation run exists."""
        return self.session.query(SQLEvaluationRun).filter(
            SQLEvaluationRun.id == evaluation_run_id
        ).count() > 0

    def delete(self, evaluation_run_id: UUID) -> bool:
        """Delete an evaluation run by ID. Returns True if deleted, False if not found."""
        db_evaluation_run = self.session.query(SQLEvaluationRun).filter(
            SQLEvaluationRun.id == evaluation_run_id
        ).first()

        if not db_evaluation_run:
            return False

        self.session.delete(db_evaluation_run)
        self.session.commit()
        return True