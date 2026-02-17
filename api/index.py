"""Vercel serverless entrypoint.

Vercel maps all `/api/*` routes to this file via `vercel.json`.
"""

from app.main import app  # noqa: F401
