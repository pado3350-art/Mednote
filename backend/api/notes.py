"""
개인 노트 CRUD API
Phase 1: 인메모리 스토어 (Phase 2에서 Supabase 실제 연동)
응답은 camelCase로 직렬화하여 TypeScript 프론트엔드와 호환
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Literal
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/notes", tags=["notes"])

# Phase 1: 인메모리 스토어
_notes_store: dict[str, dict] = {}


# ── 요청 모델 (snake_case 입력) ───────────────────────────────────

class NoteCreate(BaseModel):
    title: str
    content: str
    source_type: Literal["ai_chat", "chapter_summary", "manual"] = "manual"
    chapter_id: int | None = None
    tags: list[str] = []


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    is_public: bool | None = None


# ── 응답 모델 (camelCase 출력) ────────────────────────────────────

class NoteResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    user_id: str
    chapter_id: int | None
    title: str
    content: str
    source_type: Literal["ai_chat", "chapter_summary", "manual"]
    tags: list[str]
    is_public: bool
    created_at: str
    updated_at: str


def _to_response(doc: dict) -> NoteResponse:
    return NoteResponse(**doc)


# ── 엔드포인트 ────────────────────────────────────────────────────

@router.get("", response_model=list[NoteResponse])
async def list_notes(user_id: str = "demo-user"):
    notes = [n for n in _notes_store.values() if n["user_id"] == user_id]
    sorted_notes = sorted(notes, key=lambda n: n["created_at"], reverse=True)
    return [_to_response(n) for n in sorted_notes]


@router.post("", status_code=201, response_model=NoteResponse)
async def create_note(note: NoteCreate, user_id: str = "demo-user"):
    if not note.title.strip():
        raise HTTPException(status_code=422, detail="제목을 입력해주세요.")
    if not note.content.strip():
        raise HTTPException(status_code=422, detail="내용을 입력해주세요.")

    note_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc).isoformat()
    doc = {
        "id": note_id,
        "user_id": user_id,
        "title": note.title.strip(),
        "content": note.content.strip(),
        "source_type": note.source_type,
        "chapter_id": note.chapter_id,
        "tags": [t.strip() for t in note.tags if t.strip()],
        "is_public": False,
        "created_at": now,
        "updated_at": now,
    }
    _notes_store[note_id] = doc
    return _to_response(doc)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    if note_id not in _notes_store:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    return _to_response(_notes_store[note_id])


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, update: NoteUpdate):
    if note_id not in _notes_store:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    note = _notes_store[note_id]
    if update.title is not None:
        note["title"] = update.title.strip()
    if update.content is not None:
        note["content"] = update.content.strip()
    if update.tags is not None:
        note["tags"] = [t.strip() for t in update.tags if t.strip()]
    if update.is_public is not None:
        note["is_public"] = update.is_public
    note["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
    return _to_response(note)


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: str):
    if note_id not in _notes_store:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    del _notes_store[note_id]
