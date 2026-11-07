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
