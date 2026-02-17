"""FastAPI application.

This app is designed to work in two environments:
1) Local development with Uvicorn
2) Vercel serverless via `api/index.py`
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routers.admin import router as admin_router
from app.routers.public import router as public_router
from app.routers.push import router as push_router


def _parse_origins(raw: str) -> list[str]:
    items = [x.strip() for x in (raw or "").split(",")]
    return [x for x in items if x]


app = FastAPI(title="School Suggestions", version="1.0.0")

origins = _parse_origins(settings.CORS_ORIGINS)
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def on_startup():
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)


# API 라우트를 먼저 등록 ( catch-all 보다 앞에 있어야 함)
app.include_router(public_router)
app.include_router(admin_router)
app.include_router(push_router)


# 정적 파일 서빙 (로컬 개발용)
PUBLIC_DIR = Path(__file__).parent.parent / "public"
if PUBLIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(PUBLIC_DIR / "assets")), name="assets")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """SPA 라우팅을 위해 모든 경로를 index.html로 처리"""
    # 정적 파일이 있으면 반환
    file_path = PUBLIC_DIR / full_path
    if full_path and file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # 否则返回 index.html 用于 SPA 路由
    return FileResponse(PUBLIC_DIR / "index.html")
