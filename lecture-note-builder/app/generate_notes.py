"""Stage 3: slides + aligned script -> structured LectureNote (JSON, not DOCX).

Two backends share one interface:
  OfflineBackend    deterministic, no API; verbatim restructuring. Used for tests,
                    dry-runs, and as a safe fallback.
  AnthropicBackend  Claude with a forced tool call whose input_schema is the
                    Topic JSON schema (structured output), one call per slide chunk.
"""
from __future__ import annotations

import json
import os
from typing import Protocol

from .models import AlignedSlide, LectureNote, Slide, Statement, Topic
from .template import Template
from .transcript import time_range

EMPHASIS_CUES = ("중요", "시험", "꼭 ", "반드시", "강조", "기억", "출제", "must", "important")

SYSTEM_PROMPT = """당신은 의과대학 강의록 작성 도우미입니다. 규칙:
- 슬라이드의 모든 개념을 빠짐없이 반영하고, 분량을 줄이려고 내용을 생략하지 않는다.
- 수치·단위·약물명·cutoff는 원문 그대로 보존한다. 확립된 영어 의학 용어는 영어로 병기한다.
- 슬라이드 내용(origin=slide)과 교수 구두 설명(origin=lecturer)을 구분한다. 둘 다 근거면 both.
- 입력에 없는 의학적 주장을 추가하지 않는다. 교수 발언이 지침과 달라 보여도 조용히 고치지 말고 review_flags에 적는다.
- 모든 statement에 slide_refs와 (있다면) segment_ids를 남긴다.
- 모호하거나 전사 오류가 의심되면 review_flags에 적는다.
- sections의 키는 허용된 섹션 키만 사용한다."""


class Backend(Protocol):
    def build_topics(
        self, slides: list[Slide], aligned: dict[int, AlignedSlide], template: Template
    ) -> list[Topic]: ...


# ---------------------------------------------------------------- offline
def _is_emphasis(text: str) -> bool:
    low = text.lower()
    return any(c in low for c in EMPHASIS_CUES)


class OfflineBackend:
    def build_topics(self, slides, aligned, template):
        topics: list[Topic] = []
        for s in slides:
            a = aligned.get(s.number)
            t = Topic(
                heading=s.title or f"슬라이드 {s.number}",
                slide_numbers=[s.number],
                tables=list(s.tables),
                images=list(s.images),
            )
            core = [
                Statement(
                    text=("  " * b.level) + b.text if b.level else b.text,
                    origin="slide",
                    slide_refs=[s.number],
                )
                for b in s.body
            ]
            if s.speaker_notes:
                core.append(
                    Statement(text=f"(발표자 노트) {s.speaker_notes}", origin="slide", slide_refs=[s.number])
                )
            if core:
                t.sections["core_concepts"] = core

            adds, emph = [], []
            for g in (a.segments if a else []):
                tr = time_range(g)
                st = Statement(
                    text=g.text,
                    origin="lecturer",
                    slide_refs=[s.number],
                    segment_ids=[g.id],
                    time_ranges=[tr] if tr else [],
                    emphasis=_is_emphasis(g.text),
                )
                (emph if st.emphasis else adds).append(st)
            if adds:
                t.sections["lecturer_additions"] = adds
            if emph:
                t.sections["professor_emphasis"] = emph
            topics.append(t)
        return topics


# -------------------------------------------------------------- anthropic
class AnthropicBackend:
    def __init__(self, client=None, model: str | None = None, chunk_size: int = 3):
        if client is None:
            import anthropic  # lazy: optional dependency

            client = anthropic.Anthropic()
        self.client = client
        self.model = model or os.environ.get("MEDNOTE_MODEL", "claude-sonnet-5-5")
        self.chunk_size = chunk_size

    def _payload(self, chunk: list[Slide], aligned, template: Template) -> str:
        data = []
        for s in chunk:
            a = aligned.get(s.number)
            data.append(
                {
                    "slide": s.model_dump(exclude={"images"}),
                    "image_count": len(s.images),
                    "lecturer_segments": [
                        {"id": g.id, "time": time_range(g), "text": g.text}
                        for g in (a.segments if a else [])
                    ],
                    "alignment_confidence": a.confidence if a else None,
                }
            )
        return json.dumps(
            {
                "allowed_section_keys": {sec.key: sec.label for sec in template.sections},
                "detail_level": template.detail_level,
                "slides": data,
            },
            ensure_ascii=False,
        )

    def build_topics(self, slides, aligned, template):
        schema = Topic.model_json_schema()
        tool = {
            "name": "emit_topics",
            "description": "Return the structured lecture-note topics for these slides.",
            "input_schema": {
                "type": "object",
                "properties": {"topics": {"type": "array", "items": schema}},
                "required": ["topics"],
                "$defs": schema.get("$defs", {}),
            },
        }
        # $defs must live at the top level of the schema, not inside items.
        tool["input_schema"]["properties"]["topics"]["items"] = {
            k: v for k, v in schema.items() if k != "$defs"
        }
        topics: list[Topic] = []
        by_num = {s.number: s for s in slides}
        for i in range(0, len(slides), self.chunk_size):
            chunk = slides[i : i + self.chunk_size]
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                system=SYSTEM_PROMPT,
                tools=[tool],
                tool_choice={"type": "tool", "name": "emit_topics"},
                messages=[{"role": "user", "content": self._payload(chunk, aligned, template)}],
            )
            block = next(b for b in resp.content if getattr(b, "type", "") == "tool_use")
            for raw in block.input["topics"]:
                t = Topic.model_validate(raw)
                t.sections = {k: v for k, v in t.sections.items() if k in template.keys}
                # Images/tables are attached by code, never generated by the model.
                nums = [n for n in t.slide_numbers if n in by_num]
                t.tables = [tb for n in nums for tb in by_num[n].tables]
                t.images = [im for n in nums for im in by_num[n].images]
                topics.append(t)
        return topics


# ------------------------------------------------------------------ main
def generate_note(
    title: str,
    slides: list[Slide],
    aligned: list[AlignedSlide],
    template: Template,
    backend: Backend | None = None,
) -> LectureNote:
    backend = backend or OfflineBackend()
    amap = {a.slide_number: a for a in aligned}
    topics = backend.build_topics(slides, amap, template)

    note = LectureNote(title=title, template_name=template.template_name, topics=topics)
    for t in topics:
        for s in t.sections.get("professor_emphasis", []):
            note.exam_points.append(s)
    for a in aligned:
        if a.low_confidence_segment_ids:
            note.review_flags.append(
                f"슬라이드 {a.slide_number}: 발화 {a.low_confidence_segment_ids}의 슬라이드 매칭 "
                f"신뢰도가 낮습니다 — 확인 필요"
            )
    return note
