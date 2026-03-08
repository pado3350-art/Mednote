"""
Mednote Backend — FastAPI
약리학 학습 앱 API 서버
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api import chat, notes, review

app = FastAPI(
    title="Mednote API",
    description="Katzung 약리학 기반 학습 앱 API — 한국어 전용",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router)
app.include_router(notes.router)
app.include_router(review.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Mednote API"}
