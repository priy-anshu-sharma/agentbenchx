"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Create session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)