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


class Topic(BaseModel):
    heading: str
    slide_numbers: list[int]
    # template section key -> statements
    sections: dict[str, list[Statement]] = Field(default_factory=dict)
    tables: list[SlideTable] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)


class LectureNote(BaseModel):
    title: str
    template_name: str = ""
    topics: list[Topic] = Field(default_factory=list)
    exam_points: list[Statement] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)


# ---------- Stage 4: validation ----------
class Issue(BaseModel):
    severity: Literal["error", "warning", "info"]
    code: str
    message: str
    slide: Optional[int] = None


class ValidationReport(BaseModel):
    issues: list[Issue] = Field(default_factory=list)
    slide_coverage: float = 1.0

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def ok(self) -> bool:
        return not self.errors
