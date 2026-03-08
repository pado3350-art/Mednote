"""
간격 반복 복습 API
SM-2 알고리즘으로 복습 스케줄 계산 및 결과 기록
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

from algorithms.sm2 import calculate_next_review

router = APIRouter(prefix="/api/review", tags=["review"])

# Phase 1: 인메모리 스토어 (Phase 2에서 Supabase로 교체)
_cards_store: dict[str, dict] = {}
_logs_store: list[dict] = []


class CardCreate(BaseModel):
    note_id: str
    front: str
    back: str


class ReviewResult(BaseModel):
    card_id: str
    quality: int = Field(ge=0, le=5, description="복습 품질 점수 0~5")


@router.get("/due")
async def get_due_cards(user_id: str = "demo-user"):
    """오늘 복습할 카드 목록"""
    now = datetime.now(tz=timezone.utc).isoformat()
    due = [
        c for c in _cards_store.values()
        if c["user_id"] == user_id
        and c["is_active"]
        and c["due_date"] <= now
    ]
    return sorted(due, key=lambda c: c["due_date"])


@router.post("/cards", status_code=201)
async def create_card(card: CardCreate, user_id: str = "demo-user"):
    """노트에서 복습 카드 생성"""
    card_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc).isoformat()
    doc = {
        "id": card_id,
        "user_id": user_id,
        "note_id": card.note_id,
        "front": card.front,
        "back": card.back,
        # SM-2 초기값
        "easiness": 2.5,
        "interval": 1,
        "repetitions": 0,
        "due_date": now,
        "last_reviewed": None,
        "is_active": True,
        "created_at": now,
    }
    _cards_store[card_id] = doc
    return doc


@router.post("/result")
async def submit_review_result(result: ReviewResult, user_id: str = "demo-user"):
    """복습 결과 제출 → SM-2 계산 → 카드 업데이트"""
    card = _cards_store.get(result.card_id)
    if not card:
        raise HTTPException(status_code=404, detail="카드를 찾을 수 없습니다.")

    prev_easiness  = card["easiness"]
    prev_interval  = card["interval"]
    prev_reps      = card["repetitions"]

    sm2 = calculate_next_review(
        quality=result.quality,
        repetitions=prev_reps,
        easiness=prev_easiness,
        interval=prev_interval,
    )

    # 카드 업데이트
    now = datetime.now(tz=timezone.utc).isoformat()
    card["easiness"]     = sm2.easiness
    card["interval"]     = sm2.interval
    card["repetitions"]  = sm2.repetitions
    card["due_date"]     = sm2.next_due.isoformat()
    card["last_reviewed"] = now

    # 로그 기록
    log = {
        "id": str(uuid.uuid4()),
        "card_id": result.card_id,
        "user_id": user_id,
        "quality": result.quality,
        "prev_easiness": prev_easiness,
        "prev_interval": prev_interval,
        "new_easiness": sm2.easiness,
        "new_interval": sm2.interval,
        "next_due_date": sm2.next_due.isoformat(),
        "reviewed_at": now,
    }
    _logs_store.append(log)

    return {
        "card": card,
        "log": log,
        "message": f"다음 복습: {sm2.interval}일 후",
    }


@router.get("/stats")
async def get_stats(user_id: str = "demo-user"):
    """사용자 학습 통계"""
    today = datetime.now(tz=timezone.utc).date().isoformat()
    user_logs = [l for l in _logs_store if l["user_id"] == user_id]

    today_reviews = sum(1 for l in user_logs if l["reviewed_at"][:10] == today)
    total = len(user_logs)
    correct = sum(1 for l in user_logs if l["quality"] >= 4)
    accuracy = round(correct / total * 100, 1) if total > 0 else 0.0

    study_days = len({l["reviewed_at"][:10] for l in user_logs})
    due_today = len([
        c for c in _cards_store.values()
        if c["user_id"] == user_id
        and c["is_active"]
        and c["due_date"][:10] <= today
    ])

    return {
        "today_reviews": today_reviews,
        "accuracy": accuracy,
        "total_study_days": study_days,
        "due_today": due_today,
        "total_cards": len([c for c in _cards_store.values() if c["user_id"] == user_id]),
    }
