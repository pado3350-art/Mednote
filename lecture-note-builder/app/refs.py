"""Human-readable source references for statements."""
from __future__ import annotations

from .exam import EXAM_BASE
from .models import LectureNote


def _ranges(nums: list[int]) -> str:
    nums = sorted(set(nums))
    out, start, prev = [], None, None
    for n in nums:
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            out.append((start, prev)); start = prev = n
    if start is not None:
        out.append((start, prev))
    return ",".join(str(a) if a == b else f"{a}–{b}" for a, b in out)


def format_refs(refs: list[int], note: LectureNote, times: list[str] | None = None) -> str:
    """e.g. '발화 ¶5–7 / PAD 2022(20학번) Q1'  or  'PPT p.3,5 · 음성 01:00-01:30'."""
    normal = [r for r in refs if r < EXAM_BASE]
    exam = [note.unit_labels[r] for r in refs if r >= EXAM_BASE and r in note.unit_labels]
    parts: list[str] = []
    if normal:
        if note.ref_style == "para":
            parts.append(f"발화 ¶{_ranges(normal)}")
        else:
            parts.append(f"PPT p.{_ranges(normal)}")
    if times:
        parts.append("음성 " + ",".join(times))
    parts += exam
    return " / ".join(parts) if note.ref_style == "para" or exam else " · ".join(parts)
