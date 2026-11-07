"""Stage 1b: lecture script (TXT/DOCX) -> list[Segment].

Supported script conventions (all optional, can be mixed):
  [슬라이드 12] / [Slide 12] / #slide 12   explicit slide marker (sticky until next marker)
  [23:10] / [01:02:03] / [23:10-24:02]      timestamp at line start
Blank-line separated paragraphs become segments.
"""
from __future__ import annotations

import re
from pathlib import Path

from .models import Segment

_MARKER = re.compile(r"^\s*(?:\[|#)\s*(?:슬라이드|slide)\s*(\d+)\s*(?:\])?\s*(.*)$", re.I)
_TS = re.compile(
    r"^\s*\[?\s*((?:\d{1,2}:)?\d{1,2}:\d{2})(?:\s*[-–~]\s*((?:\d{1,2}:)?\d{1,2}:\d{2}))?\s*\]?\s*(.*)$"
)


def parse_ts(s: str) -> float:
    parts = [int(p) for p in s.split(":")]
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return float(sec)


def fmt_ts(sec: float) -> str:
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def read_script_text(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".docx":
        from docx import Document

        return "\n".join(p.text for p in Document(str(path)).paragraphs)
    return path.read_text(encoding="utf-8-sig")


def parse_script(text: str) -> list[Segment]:
    segments: list[Segment] = []
    current_hint: int | None = None
    buf: list[str] = []
    start = end = None
    seg_hint: int | None = None

    def flush():
        nonlocal buf, start, end
        body = " ".join(buf).strip()
        if body:
            segments.append(
                Segment(id=len(segments), text=body, start=start, end=end, slide_hint=seg_hint)
            )
        buf, start, end = [], None, None

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        m = _MARKER.match(line)
        if m:
            flush()
            current_hint = int(m.group(1))
            seg_hint = current_hint
            rest = m.group(2).strip()
            if rest:
                buf.append(rest)
            continue
        t = _TS.match(line)
        if t:
            flush()
            seg_hint = current_hint
            start = parse_ts(t.group(1))
            end = parse_ts(t.group(2)) if t.group(2) else None
            rest = t.group(3).strip()
            if rest:
                buf.append(rest)
            continue
        seg_hint = seg_hint if buf else current_hint
        buf.append(line.strip())
    flush()
    # Infer missing end times from the next segment's start.
    for a, b in zip(segments, segments[1:]):
        if a.start is not None and a.end is None and b.start is not None:
            a.end = b.start
    return segments


def time_range(seg: Segment) -> str | None:
    if seg.start is None:
        return None
    return fmt_ts(seg.start) + (f"-{fmt_ts(seg.end)}" if seg.end is not None else "")


# --------------------------------------------------------------------------
# Structured script: "[00:00–02:00] 제목  |  원본 2쪽" headed blocks, as produced by
# reconstructed/segmented lecture scripts. Each block becomes one *unit* (the
# script-only equivalent of a slide).
# --------------------------------------------------------------------------
from dataclasses import dataclass, field  # noqa: E402

# Block header: "[00:00–02:00] 제목  |  원본 2쪽"  or  "00:00–02:00 | 제목" (brackets / source page optional).
# The title must be short (<= 70 chars) so that long speech lines starting with a time range are not mistaken for headers.
_UNIT_HDR = re.compile(
    r"^\s*\[?(\d{1,2}:\d{2})\s*[–\-~]\s*(\d{1,2}:\d{2})\]?\s*\|?\s*(.{1,70}?)\s*(?:\|\s*원본\s*([\d–\-, ]+)\s*쪽)?\s*$"
)
_PAGES_LINE = re.compile(r"^\s*(?:자료\s*기준|원본)\s*[:：]?\s*([\d–\-, ]+)\s*쪽\s*$")
_TRAILER_HDR = re.compile(r"^\s*(재구성\s*및\s*검증\s*참고|검증\s*참고|자료\s*충실도\s*및\s*제한)\s*$")
_LECTURE_REF = re.compile(
    r"「\s*(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})\s+(?:(\S+?)\s+[—–-]\s+|(\S+)\s+)(.+?)\s*」")
_DATE = re.compile(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})")


@dataclass
class Unit:
    number: int
    title: str
    start: float | None
    end: float | None
    pages: str
    paragraphs: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        t = f"{fmt_ts(self.start)}–{fmt_ts(self.end)}" if self.start is not None else "검증 참고"
        return t + (f" · 원본 {self.pages}쪽" if self.pages else "")


def is_structured(text: str) -> bool:
    return sum(1 for ln in text.splitlines() if _UNIT_HDR.match(ln)) >= 3


def parse_structured_script(text: str) -> tuple[dict[str, str], list[Unit]]:
    meta: dict[str, str] = {}
    units: list[Unit] = []
    cur: Unit | None = None
    preamble: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        h = _UNIT_HDR.match(line)
        if h:
            cur = Unit(len(units) + 1, h.group(3).strip(), parse_ts(h.group(1)), parse_ts(h.group(2)),
                       (h.group(4) or "").strip())
            units.append(cur)
        elif cur is not None and cur.start is not None and not cur.paragraphs and _PAGES_LINE.match(line):
            cur.pages = _PAGES_LINE.match(line).group(1).strip()
        elif _TRAILER_HDR.match(line):
            cur = Unit(len(units) + 1, "재구성 및 검증 참고", None, None, "")
            units.append(cur)
        elif cur is None:
            preamble.append(line)
        else:
            cur.paragraphs.append(line.lstrip("•").strip() if cur.start is None else line)
    if preamble:
        meta["title"] = re.split(r"\s+[—–-]\s+", preamble[0])[0].strip()
    for ln in preamble:
        ref = _LECTURE_REF.search(ln)
        if ref and "date" not in meta:
            d = re.match(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", ref.group(1))
            meta["date"] = f"{int(d.group(1)):04d}-{int(d.group(2)):02d}-{int(d.group(3)):02d}"
            meta["subject"] = ref.group(2) or ref.group(3)
            meta["title"] = ref.group(4).strip()
            continue
        m = _DATE.search(ln)
        if m and "date" not in meta:
            meta["date"] = f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
            tail = ln[m.end():]
            subj = re.search(r"([가-힣A-Za-z]+)\s*[—\-–]", tail)
            if subj:
                meta["subject"] = subj.group(1)
        if ln.startswith("주의"):
            meta["source_caveat"] = ln.removeprefix("주의:").strip()
    return meta, units


def read_docx_tables(path: str | Path) -> list[list[list[str]]]:
    from docx import Document

    return [[[c.text.strip() for c in r.cells] for r in t.rows] for t in Document(str(path)).tables]


def parse_flow_script(text: str) -> tuple[dict[str, str], list[Segment]]:
    """Script-only mode: the lecture is read as ONE continuous flow of paragraphs.

    Time-block headers ("[00:00–02:00] 제목 | 원본 2쪽") are NOT used to section the lecture;
    they are dropped (the AI decides the table of contents from the flow). Trailing
    "재구성 및 검증 참고" remarks become kind="note" segments (appendix material).
    """
    meta: dict[str, str] = {}
    segs: list[Segment] = []
    if is_structured(text):
        meta, units = parse_structured_script(text)
        for u in units:
            for para in u.paragraphs:
                segs.append(Segment(id=len(segs) + 1, text=para, kind="speech" if u.start is not None else "note"))
        return meta, segs
    for g in parse_script(text):
        segs.append(Segment(id=len(segs) + 1, text=g.text, kind="speech"))
    return meta, segs
