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
    fig_captions: list[str] = Field(default_factory=list)  # "Fig. 6.x ..." lines of the slide (material DOCX)

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
class Group(BaseModel):
    """One box of a diagram: tree branch / flow stage / compare column. Text supports the inline markup
    ({r|..} red, {b|..} BLUE = PAD only, {g|..} gray, {p|..} purple, **bold**)."""
    title: str
    items: list[str] = Field(default_factory=list)
    color: str = ""  # teal | blue | salmon | amber | violet | gray (default: cycle)
    image: str = ""  # original picture path for a `columns` panel


class Arrow(BaseModel):
    src: int  # group index
    dst: int
    label: str = ""
    both: bool = False  # two-way arrow (reciprocal connection)


class Diagram(BaseModel):
    """Schematic drawn by the program (no image needed): concept tree, left-to-right flow, comparison cards."""
    kind: Literal["tree", "flow", "compare", "pyramid", "cycle"] = "tree"
    # pyramid: hierarchy, groups top (narrow, highest) -> bottom (wide), `root` = axis label (e.g. "분화능 ↑")
    # cycle: groups around a circle with arrows i -> i+1 (last -> first), `root` = text in the middle
    size: Literal["full", "side"] = "full"  # side = narrow canvas for a figure_side / concept box (bigger text)
    title: str = ""
    root: str = ""  # tree: text of the top box
    groups: list[Group] = Field(default_factory=list)
    arrows: list[Arrow] = Field(default_factory=list)  # flow: arrows between groups
    row_labels: list[str] = Field(default_factory=list)  # compare: label per row


class Statement(BaseModel):
    text: str
    origin: Literal["slide", "lecturer", "both", "author"] = "slide"  # author = note writer's own addition (analogy, tip); shown in ( )
    slide_refs: list[int] = Field(default_factory=list)
    segment_ids: list[int] = Field(default_factory=list)
    time_ranges: list[str] = Field(default_factory=list)  # e.g. "23:10-24:02"
    emphasis: bool = False
    # Visual role (MOM colour legend): exam=BLUE (기출 only!), minor=gray, verify=purple;
    # red is `emphasis`. Blue requires a PAD (기출) source ref -> see validate_notes.
    tag: Literal["normal", "exam", "exam_other", "minor", "verify"] = "normal"
    # Layout role: paragraph, "-" bullet, "★" sub-heading, or an Advice / Reference call-out.
    kind: Literal["para", "bullet", "star", "advice", "reference", "figure", "diagram", "row2", "quiz", "figure_side", "columns", "check", "concept", "rows", "qa", "callout", "sub"] = "para"
    level: int = 0
    image: str = ""  # kind == "figure"/"diagram": picture path (text = caption)
    # kind == "row2": one row of the two-column "slide table" (left = slide / English original, right = explanation in `text`)
    left_title: str = ""
    left: list[str] = Field(default_factory=list)  # lines, "- " prefix = bullet; same markup as text
    # kind == "quiz": `text` = case / stem, options, `answer` = correct answer (+ short reason)
    options: list[str] = Field(default_factory=list)
    answer: str = ""  # quiz: correct answer text; check: "O" or "X"
    explanations: list[str] = Field(default_factory=list)  # quiz: per-option explanation (mark the right one "(정답)"); check: reason
    # How much effort this deserves (the lecturer's cue): 필수 = memorise, 이해 = understand, 참고 = just know it exists
    effort: Literal["", "필수", "이해", "참고"] = ""
    rows: list[list[str]] = Field(default_factory=list)
    col_titles: list[str] = Field(default_factory=list)
    col_widths: list[float] = Field(default_factory=list)
    diagram: Optional["Diagram"] = None  # kind == "diagram": spec rendered to a picture by app/design/diagrams.py
    # kind == "check": `text` = statement to judge, `answer` = "O"/"X", `left_title` = one-line summary of the page/§
    #   (shown once above the group), `explanations[0]` = why (shown in the answer box). Answers are printed at the end of the topic.
    # kind == "concept": grey "개념 정리" box: `left_title` = title, `left` = lines
    # kind == "figure_side": picture (`image`, caption = `text`) beside a bullet box (`left_title`, `left` lines)
    # kind == "columns": `diagram.groups` holds ordered panels (title, optional image, observations in items)
    # kind == "rows": a table (L16): `rows` = [[label, cell, ...], ...] (cell text: markup, "\n" = new line, "- " = bullet,
    #   "→ x" lines are plain), `col_titles` = optional header row, `col_widths` = optional widths in cm
    # kind == "callout" (L33): a thin-ruled box with a bracketed title - `left_title` = "작성자 추가설명" / "작성자가 헷갈려서 정리" /
    #   "잠깐 정리하고 가기" / "ppt에는 없는 여담 - 소제목" / "Ppt 내용 추가", `left` = body lines (markup, "- " = bullet)
    # kind == "sub" (L31): the (1) / (2) sub-heading LINE inside a §: green-marked label before " = " / " : ", rest bold, e.g.
    #   "(1) 정상 안구 정렬 = bifoveal fixation★"
    # kind == "qa": the lecturer's own question in a yellow box (`left_title` = "질문1" / "역질문2", `text` = the question)
    #   followed by the answer lines in `left` ("A. ...")


class Topic(BaseModel):
    heading: str
    chapter: str = ""  # chapter title (no number); topics sharing it are grouped as "§ 1, § 2 ..."
    role: Literal["body", "front", "closing"] = "body"  # front = 요약 pages (not in the TOC); closing = "Take home messages" chapter (L30)
    basics_title: str = ""  # 기본정석 box title
    basics: list[str] = Field(default_factory=list)  # 기본정석 box: 2-4 core points of the §
    basics_refs: list[int] = Field(default_factory=list)  # sources of the box; PAD units here allow BLUE inside it
    mark: str = ""  # exam marker shown in red next to the heading, e.g. "출제예고 · 짤" / "중요언급" (the human MOM puts ⭐ markers there)
    new_page: bool = False  # start this § on a new page (a § built around one big figure / table: one anchor per page)
    tip: str = ""  # study-priority hint shown as a yellow-highlighted line under the 기본정석 box
    slide_numbers: list[int]
    # template section key -> statements
    sections: dict[str, list[Statement]] = Field(default_factory=dict)
    tables: list[SlideTable] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    # mixed style (default): "explain" = question heading + 핵심 답 + reasoning paragraphs,
    # "list" = bullets / columns / tables + "즉 …" line. "" = not decided (non-mixed templates)
    style: Literal["", "explain", "list"] = ""


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
    pad_professors: dict[int, str] = Field(default_factory=dict)  # PAD unit -> professor (two-blue rule)
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
