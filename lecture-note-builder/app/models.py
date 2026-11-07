"""Shared data models. Every stage reads/writes these, so each stage's
output can be saved as JSON and re-run independently (partial regeneration)."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------- Stage 1: slides ----------
class BodyLine(BaseModel):
    text: str
    level: int = 0


class SlideTable(BaseModel):
    rows: list[list[str]]
    caption: str = ""
    heat_cols: list[int] = Field(default_factory=list)  # shade numeric columns (white->red)
    col_widths_cm: list[float] = Field(default_factory=list)  # optional column widths


class Slide(BaseModel):
    number: int  # 1-based, matches PowerPoint's slide numbering
    title: str = ""
    body: list[BodyLine] = Field(default_factory=list)
    tables: list[SlideTable] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)  # file paths
    speaker_notes: str = ""

    def plain_text(self, include_notes: bool = True) -> str:
        parts = [self.title] + [b.text for b in self.body]
        for t in self.tables:
            parts += [" ".join(r) for r in t.rows]
        if include_notes and self.speaker_notes:
            parts.append(self.speaker_notes)
        return "\n".join(p for p in parts if p)


# ---------- Stage 2: transcript / alignment ----------
class Segment(BaseModel):
    id: int
    text: str
    start: Optional[float] = None  # seconds
    end: Optional[float] = None
    slide_hint: Optional[int] = None  # explicit marker in the script
    kind: Literal["speech", "note"] = "speech"  # "note" = meta remarks about the script itself


class AlignedSlide(BaseModel):
    slide_number: int
    segments: list[Segment] = Field(default_factory=list)
    confidence: float = 1.0  # min confidence among its segments (1.0 if none)
    method: Literal["marker", "similarity", "none"] = "none"
    low_confidence_segment_ids: list[int] = Field(default_factory=list)


# ---------- Stage 3: structured notes ----------
class Statement(BaseModel):
    text: str
    origin: Literal["slide", "lecturer", "both"] = "slide"
    slide_refs: list[int] = Field(default_factory=list)
    segment_ids: list[int] = Field(default_factory=list)
    time_ranges: list[str] = Field(default_factory=list)  # e.g. "23:10-24:02"
    emphasis: bool = False
    # Visual role (MOM colour legend): exam=BLUE (기출 only!), minor=gray, verify=purple;
    # red is `emphasis`. Blue requires a PAD (기출) source ref -> see validate_notes.
    tag: Literal["normal", "exam", "minor", "verify"] = "normal"
    # Layout role: paragraph, "-" bullet, "★" sub-heading, or an Advice / Reference call-out.
    kind: Literal["para", "bullet", "star", "advice", "reference", "figure"] = "para"
    level: int = 0
    image: str = ""  # kind == "figure": picture path (text = caption)


class Topic(BaseModel):
    heading: str
    chapter: str = ""  # chapter title (no number); topics sharing it are grouped as "§ 1, § 2 ..."
    role: Literal["body", "front"] = "body"  # front = 핵심 어휘 / 요약 정리 pages (not in the TOC)
    basics_title: str = ""  # 기본정석 box title
    basics: list[str] = Field(default_factory=list)  # 기본정석 box: 2-4 core points of the §
    basics_refs: list[int] = Field(default_factory=list)  # sources of the box; PAD units here allow BLUE inside it
    slide_numbers: list[int]
    # template section key -> statements
    sections: dict[str, list[Statement]] = Field(default_factory=dict)
    tables: list[SlideTable] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)


class Figure(BaseModel):
    """A picture taken from lecture material (slides, handout PDF, photo folder) + where it was placed."""
    id: int
    path: str
    source: str = ""  # file name
    page: int = 0
    caption: str = ""
    context: str = ""  # surrounding text on the source page (used to match it to a section)
    near: str = ""  # text right next to the picture (used to pick the anchor statement)
    width: int = 0
    height: int = 0
    unit: Optional[int] = None  # slide/page number: figure belongs to that unit (direct placement)
    topic: Optional[int] = None  # placement result: index into note.topics
    after: Optional[int] = None  # inserted after this statement index of the topic (-1 = start)
    score: float = 0.0
    skip: bool = False
    topic_heading: str = ""  # manual: section whose heading contains this text
    anchor: str = ""  # manual: place after the "★" block whose sub-heading contains this text
    text_like: bool = False  # mostly black text on white (a slide of bullet points): skipped unless asked


class LectureNote(BaseModel):
    title: str
    template_name: str = ""
    topics: list[Topic] = Field(default_factory=list)
    exam_points: list[Statement] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    # Cover-page info for the MOM layout: date ("2023-04-26"), subject,
    # professor, author, comment (free text).
    meta: dict[str, str] = Field(default_factory=dict)
    # Script-only mode: unit number -> "04:00–06:00 · 원본 4쪽" (replaces "PPT p.N").
    unit_labels: dict[int, str] = Field(default_factory=dict)
    # How unit numbers are shown: "slide" -> PPT p.N, "para" -> 발화 ¶N (script-only mode).
    ref_style: Literal["slide", "para"] = "slide"
    figures: list[Figure] = Field(default_factory=list)  # placement log (figures.json)


class OutlineItem(BaseModel):
    heading: str
    unit_numbers: list[int]  # slides, or script paragraphs (1-based) in script-only mode
    chapter: str = ""  # optional chapter this section belongs to
    summary: str = ""


class Outline(BaseModel):
    """AI-judged table of contents: how the lecture's overall flow is sectioned."""
    items: list[OutlineItem] = Field(default_factory=list)


# ---------- Stage 4: validation ----------
class Issue(BaseModel):
    severity: Literal["error", "warning", "info"]
    code: str
    message: str
    slide: Optional[int] = None


class ValidationReport(BaseModel):
    issues: list[Issue] = Field(default_factory=list)
    slide_coverage: float = 1.0
    unit_names: dict[int, str] = Field(default_factory=dict)  # unit number -> "발화 ¶7" etc.

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors
