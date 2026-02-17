"""SQLAlchemy session/engine setup."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Database URL processing for Vercel
database_url = settings.DATABASE_URL

# Auto-convert to pg8000 for Vercel compatibility
if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

# SQLite settings
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
