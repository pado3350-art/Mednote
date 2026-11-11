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
import re
from typing import Protocol

from ..pad.exam import EXAM_BASE, ExamItem
from ..models import AlignedSlide, LectureNote, Outline, SlideTable, Slide, Statement, Topic
from ..template import Template
from .transcript import time_range

EMPHASIS_CUES = ("중요", "시험", "꼭 ", "반드시", "강조", "기억", "출제", "must", "important")

def load_style_guide() -> str:
    """Rules of the `readable-note-organizer` skill (single source of truth for the writing style)."""
    from pathlib import Path

    p = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "readable-note-organizer" / "SKILL.md"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return ""
    guide = re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.S)
    return guide + learned_rules()


def learned_rules(lecture_type: str = "") -> str:
    """Rules the USER APPROVED from their own edits (app/write/feedback.py). Empty when none are approved, so the
    generator is unchanged until the user approves something; pending candidates are never read."""
    try:
        from .feedback import approved_rules_markdown

        text = approved_rules_markdown(lecture_type)
    except Exception:  # a broken rule file must never stop note generation
        return ""
    return ("\n\n" + text) if text else ""


SYSTEM_PROMPT = """당신은 의과대학 강의록 작성 도우미입니다. 규칙:
- 슬라이드의 모든 개념을 빠짐없이 반영하고, 분량을 줄이려고 내용을 생략하지 않는다.
- 수치·단위·약물명·cutoff는 원문 그대로 보존한다. 확립된 영어 의학 용어는 영어로 병기한다.
- 슬라이드 내용(origin=slide)과 교수 구두 설명(origin=lecturer)을 구분한다. 둘 다 근거면 both.
- 입력에 없는 의학적 주장을 추가하지 않는다. 교수 발언이 지침과 달라 보여도 조용히 고치지 말고 review_flags에 적는다.
- 모든 statement에 slide_refs와 (있다면) segment_ids를 남긴다.
- 모호하거나 전사 오류가 의심되면 review_flags에 적는다.
- sections의 키는 허용된 섹션 키만 사용한다.
- 인라인 서식: {r|빨강=교수 강조·시험 언급} {g|회색=덜 중요} {p|보라=검증 필요} **굵게**.
- [무조건 규칙] 파랑 {b|...} = 입력의 pad_questions(기출문제)에 실제로 나온 내용 ONLY. pad_questions가 있으면 그 문제·정답·해설에 해당하는 모든 내용을 빠짐없이 파랑으로 쓰고 slide_refs에 해당 PAD 번호(unit)를 넣는다. PAD가 없으면 파랑을 쓰지 않는다. 일반 용어 강조에는 굵게를 쓴다. 기본정석 박스의 파랑도 같은 규칙(basics_refs에 PAD 번호).
- 입력 단락은 번호(unit)로 인용한다(slide_refs). 한 섹션의 모든 단락 내용을 빠짐없이 반영한다.
- 받아쓰기가 아니라 '이해하기 쉽게 정리'한다 (아래 스타일 가이드). 각 섹션에 basics_title과 basics(기본정석 2~4줄)를 채운다."""


class Backend(Protocol):
    def build_topics(
        self, slides: list[Slide], aligned: dict[int, AlignedSlide], template: Template,
        outline: Outline | None = None, exam: list[ExamItem] | None = None,
    ) -> list[Topic]: ...


def _key(template: Template, preferred: str) -> str:
    return preferred if preferred in template.keys else template.keys[0]


def exam_topic(items: list[ExamItem], template: Template) -> Topic:
    """Code-built section for PAD (기출): blue statements + list table. Always cites PAD units."""
    key = _key(template, "core_concepts")
    sts: list[Statement] = []
    rows = [["연도(학번)", "문제 (요약)", "정답"]]
    for it in items:
        q = re.split(r"\s(?:①|1\)|1\.)\s", it.question)[0].strip()
        sts.append(Statement(text=f"{{b|**{it.year}년 {it.cohort}** {q} → 정답 {it.answer}}}",
                             slide_refs=[it.number], origin="both", kind="bullet"))
        if it.commentary:
            sts.append(Statement(text=f"{{g|{it.commentary}}}", slide_refs=[it.number], origin="both",
                                 kind="bullet", level=1))
        rows.append([f"{it.year}년({it.cohort})", q[:60], it.answer])
    return Topic(heading="0. 기출(PAD) & 시험 포인트", slide_numbers=[i.number for i in items],
                 sections={key: sts}, tables=[SlideTable(rows=rows, col_widths_cm=[3.6, 10.2, 3.6],
                                                         caption="기출 문항 목록 (정답은 PAD 기재 기준)")])


# ---------------------------------------------------------------- offline
def _is_emphasis(text: str) -> bool:
    low = text.lower()
    return any(c in low for c in EMPHASIS_CUES)


class OfflineBackend:
    """No API needed. With an outline (script-only mode) the text is *organised* by rules
    (app/write/offline_organizer.py); `organize=False` keeps the verbatim paragraphs."""

    def __init__(self, organize: bool = True, auto_blue: bool = True):
        self.organize = organize
        self.auto_blue = auto_blue  # match sentences against the PAD and colour them blue (approximate!)

    def make_front(self, topics, template):
        from .offline_organizer import make_front_pages

        return make_front_pages(topics, _key(template, "core_concepts")) if self.organize else []

    def build_topics(self, slides, aligned, template, outline=None, exam=None):
        if template.format.slide_table and any(s.title for s in slides if s.number < EXAM_BASE):
            return self._slide_table_topics(slides, aligned, template, outline)  # slide | explanation rows
        if outline is not None:  # script-flow mode: paragraphs grouped under the outline
            by = {s.number: s for s in slides}
            key = _key(template, "core_concepts")
            if self.organize:
                from .offline_organizer import organize_section, term_allowlist
                from ..pad.pad_match import PadMatcher

                sections = [[by[n] for n in it.unit_numbers if n in by] for it in outline.items]
                allowed = term_allowlist(sections)
                matcher = PadMatcher(exam) if (exam and self.auto_blue) else None
                topics = [organize_section(units, it.heading, it.chapter, allowed[i], matcher)
                          for i, (units, it) in enumerate(zip(sections, outline.items))]
                for t in topics:  # the organizer writes into "body"; map to the template's main section
                    if key != "body":
                        t.sections = {key: t.sections.pop("body")}
                return topics
            out: list[Topic] = []
            for it in outline.items:
                sts = [Statement(text=b.text, origin="lecturer", slide_refs=[n])
                       for n in it.unit_numbers if n in by for b in by[n].body]
                out.append(Topic(heading=it.heading, chapter=it.chapter, slide_numbers=list(it.unit_numbers), sections={key: sts}))
            return out
        if template.format.slide_table and any(s.title for s in slides if s.number < EXAM_BASE):
            return self._slide_table_topics(slides, aligned, template, outline)  # slide | explanation rows
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


def _slide_table_topics(self, slides, aligned, template, outline=None):
    """One two-column row per slide (left = slide text, right = lecturer explanation). With an outline several
    slides share a page (one topic per section), as in the clinical example notes."""
    from .offline_organizer import clean_sentences

    key = _key(template, "core_concepts")
    by = {s.number: s for s in slides}
    if outline is not None:
        groups = [(it.heading, it.chapter, [by[n] for n in it.unit_numbers if n in by]) for it in outline.items]
    else:
        groups = [(s.title or f"슬라이드 {s.number}", "", [s]) for s in slides if s.number < EXAM_BASE]
    topics: list[Topic] = []
    for heading, chapter, group in groups:
        rows: list[Statement] = []
        for s in group:
            a = aligned.get(s.number)
            left = ["- " + "  " * b.level + b.text for b in s.body]
            for tb in s.tables:
                left += ["- " + " | ".join(r) for r in tb.rows]
            paras = []
            for g in (a.segments if a else []):
                sents = clean_sentences(g.text)
                if sents:
                    txt = " ".join(sents)
                    paras.append("- " + ("{r|" + txt + "}" if any(c in txt for c in EMPHASIS_CUES) else txt))
            right = "\n".join(paras) if paras else "{g|교수님 설명 없음 — 슬라이드만 제시됨}"
            rows.append(Statement(text=right, kind="row2", left_title=s.title or f"슬라이드 {s.number}", left=left or [""],
                                  origin="both", slide_refs=[s.number],
                                  segment_ids=[g.id for g in (a.segments if a else [])]))
        topics.append(Topic(heading=heading, chapter=chapter, slide_numbers=[s.number for s in group],
                            sections={key: rows}))
    return topics


OfflineBackend._slide_table_topics = _slide_table_topics


# ------------------------------------------------------------ precomputed
class PrecomputedBackend:
    """Use topics authored elsewhere (e.g. by Claude Code in a session, or a
    hand-edited note.json). Lets the renderer/validator run without an API."""

    def __init__(self, topics: list[Topic]):
        self.topics = topics

    @classmethod
    def from_json(cls, path) -> "PrecomputedBackend":
        import json
        from pathlib import Path

        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        raw = raw["topics"] if isinstance(raw, dict) else raw
        return cls([Topic.model_validate(t) for t in raw])

    authors_exam = True  # the authored note already contains its own PAD section

    def build_topics(self, slides, aligned, template, outline=None, exam=None):
        return self.topics


# -------------------------------------------------------------- anthropic
class AnthropicBackend:
    def __init__(self, client=None, model: str | None = None, chunk_size: int = 3):
        if client is None:
            import anthropic  # lazy: optional dependency

            client = anthropic.Anthropic()
        self.client = client
        self.model = model or os.environ.get("MEDNOTE_MODEL", "claude-sonnet-5-5")
        self.chunk_size = chunk_size

    def make_outline(self, units: list[Slide], exam: list[ExamItem] | None = None) -> Outline:
        from .outline import AnthropicOutliner

        hint = [f"{e.year} {e.question[:50]}" for e in (exam or [])]
        return AnthropicOutliner(self.client, self.model).make_outline(units, hint)

    def make_front(self, topics: list[Topic], template: Template) -> list[Topic]:
        """핵심 어휘 + 요약 정리 pages, written from the finished sections."""
        key = _key(template, "core_concepts")
        digest = [{"chapter": t.chapter, "heading": t.heading, "basics": t.basics,
                   "text": [re.sub(r"[{}]|\w\|", "", st.text) for sts in t.sections.values() for st in sts]}
                  for t in topics]
        schema = Topic.model_json_schema()
        tool = {"name": "emit_front", "description": "Return the two front pages.", "input_schema": {
            "type": "object", "properties": {"topics": {"type": "array", "items": {k: v for k, v in schema.items() if k != "$defs"}}},
            "required": ["topics"], "$defs": schema.get("$defs", {})}}
        resp = self.client.messages.create(
            model=self.model, max_tokens=6000,
            system=SYSTEM_PROMPT + "\n\n## 스타일 가이드\n" + load_style_guide() + "\n\n" +
            "지금 작업: 완성된 섹션들을 읽고 앞쪽 두 페이지를 만든다. topics는 정확히 2개: heading='핵심 어휘'(핵심 용어 한 줄 정의, 교수가 언급한 것만, 전부 slide_refs 포함)와 heading='요약 정리'(섹션별 치트시트 + 도식 2~4개: kind='diagram'의 diagram에 tree(개념 지도)/flow(경로·순서, arrows)/compare(비교 카드, row_labels)). 도식 안의 파랑{b|}은 PAD 내용만이며 그 statement의 slide_refs에 PAD 번호가 있어야 한다. role='front'.",
            tools=[tool], tool_choice={"type": "tool", "name": "emit_front"},
            messages=[{"role": "user", "content": json.dumps({"sections": digest}, ensure_ascii=False)}],
        )
        block = next(b for b in resp.content if getattr(b, "type", "") == "tool_use")
        out = []
        for raw in block.input["topics"]:
            t = Topic.model_validate(raw)
            t.role = "front"
            t.chapter = ""
            t.sections = {key: [st for v in t.sections.values() for st in v]} if t.sections else {}
            out.append(t)
        return out

    def _payload(self, chunk: list[Slide], aligned, template: Template, exam=None, heading=None) -> str:
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
                "section_heading": heading,
                "slides": data,
                "pad_questions": [
                    {"unit": e.number, "year": e.year, "question": e.question, "answer": e.answer,
                     "commentary": e.commentary} for e in (exam or [])
                ],
            },
            ensure_ascii=False,
        )

    def build_topics(self, slides, aligned, template, outline=None, exam=None):
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
        if outline is not None:  # one call per AI-outlined section
            groups = [([by_num[n] for n in it.unit_numbers if n in by_num], it) for it in outline.items]
        else:
            groups = [(slides[i : i + self.chunk_size], None) for i in range(0, len(slides), self.chunk_size)]
        for chunk, item in groups:
            if not chunk:
                continue
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                system=SYSTEM_PROMPT + "\n\n## 스타일 가이드\n" + load_style_guide(),
                tools=[tool],
                tool_choice={"type": "tool", "name": "emit_topics"},
                messages=[{"role": "user", "content": self._payload(
                    chunk, aligned, template, exam, item.heading if item else None)}],
            )
            block = next(b for b in resp.content if getattr(b, "type", "") == "tool_use")
            made: list[Topic] = []
            for raw in block.input["topics"]:
                t = Topic.model_validate(raw)
                t.sections = {k: v for k, v in t.sections.items() if k in template.keys}
                made.append(t)
            if item is not None:  # merge into ONE topic that follows the outline exactly
                merged = Topic(heading=item.heading, chapter=item.chapter, slide_numbers=list(item.unit_numbers))
                for t in made:
                    for k, v in t.sections.items():
                        merged.sections.setdefault(k, []).extend(v)
                    merged.review_flags += t.review_flags
                    merged.basics = merged.basics or t.basics
                    merged.basics_title = merged.basics_title or t.basics_title
                made = [merged]
            for t in made:
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
    meta: dict[str, str] | None = None,
    unit_labels: dict[int, str] | None = None,
    outline: Outline | None = None,
    exam_items: list[ExamItem] | None = None,
    ref_style: str = "slide",
) -> LectureNote:
    backend = backend or OfflineBackend()
    amap = {a.slide_number: a for a in aligned}
    topics = backend.build_topics(slides, amap, template, outline=outline, exam=exam_items)
    if exam_items and template.format.exam_section and not getattr(backend, "authors_exam", False):
        topics = [exam_topic(exam_items, template), *topics]
    make_front = getattr(backend, "make_front", None)
    if make_front and outline is not None:  # 핵심 어휘 / 요약 정리 pages written from the finished sections
        topics = [*make_front(topics, template), *topics]

    note = LectureNote(
        title=title, template_name=template.template_name, topics=topics,
        meta=meta or {}, unit_labels=unit_labels or {}, ref_style=ref_style,
    )
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
