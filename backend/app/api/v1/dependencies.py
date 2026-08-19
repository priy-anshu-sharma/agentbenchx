"""API dependencies for AgentBenchX backend."""

from typing import Generator

from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()