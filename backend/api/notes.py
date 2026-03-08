"""
개인 노트 CRUD API
Phase 1: 기본 CRUD 구조 (Phase 2에서 Supabase 실제 연동)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/notes", tags=["notes"])

# Phase 1: 인메모리 스토어 (Phase 2에서 Supabase로 교체)
_notes_store: dict[str, dict] = {}


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


@router.get("")
async def list_notes(user_id: str = "demo-user"):
    notes = [n for n in _notes_store.values() if n["user_id"] == user_id]
    return sorted(notes, key=lambda n: n["created_at"], reverse=True)


@router.post("", status_code=201)
async def create_note(note: NoteCreate, user_id: str = "demo-user"):
    note_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc).isoformat()
    doc = {
        "id": note_id,
        "user_id": user_id,
        "title": note.title,
        "content": note.content,
        "source_type": note.source_type,
        "chapter_id": note.chapter_id,
        "tags": note.tags,
        "is_public": False,
        "created_at": now,
        "updated_at": now,
    }
    _notes_store[note_id] = doc
    return doc


@router.get("/{note_id}")
async def get_note(note_id: str):
    if note_id not in _notes_store:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    return _notes_store[note_id]


@router.patch("/{note_id}")
async def update_note(note_id: str, update: NoteUpdate):
    if note_id not in _notes_store:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    note = _notes_store[note_id]
    if update.title is not None:
        note["title"] = update.title
    if update.content is not None:
        note["content"] = update.content
    if update.tags is not None:
        note["tags"] = update.tags
    if update.is_public is not None:
        note["is_public"] = update.is_public
    note["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
    return note


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: str):
    if note_id not in _notes_store:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    del _notes_store[note_id]
