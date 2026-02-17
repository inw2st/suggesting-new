"""SQLAlchemy session/engine setup."""

from __future__ import annotations

import ssl
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Database URL processing for Vercel
database_url = settings.DATABASE_URL

# Auto-convert to pg8000 for Vercel compatibility
if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

# sslmode 파라미터를 URL에서 제거 (pg8000은 connect_args로만 SSL 처리)
if database_url.startswith("postgresql"):
    parsed = urlparse(database_url)
    qs = parse_qs(parsed.query)
    qs.pop("sslmode", None)  # sslmode 제거
    new_query = urlencode({k: v[0] for k, v in qs.items()})
    database_url = urlunparse(parsed._replace(query=new_query))

# SQLite settings
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif database_url.startswith("postgresql"):
    # pg8000은 ssl_context 객체로 SSL 처리
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl_context": ssl_context}

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