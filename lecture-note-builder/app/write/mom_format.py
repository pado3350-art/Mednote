"""Fixed skeleton and call-out boxes of the human MOM '사시' (approved rules L30-L34, docs/design_mom_format.md).

  cover   작성자 코멘트 -> 목차 -> [강조점 세가지]        (meta.points)
  body    Ⅰ. 장 -> [1] 소절 -> (1) 소소제목 줄(kind "sub") -> ① 라벨 줄
  boxes   [작성자 추가설명] [막간 퀴즈] [작성자가 헷갈려서 정리] [잠깐 정리하고 가기]   (kind "callout" / "qa")
  PPT     [ppt에는 없는 여담 - 소제목] [Ppt 내용 추가] (only when the lecture HAS slide text; a script-only lecture has neither)
  close   Ⅲ. Take home messages                         (Topic.role "closing")
"""
from __future__ import annotations

import re

from ..models import LectureNote

CALLOUT_TITLES = ("작성자 추가설명", "작성자가 헷갈려서 정리", "잠깐 정리하고 가기", "ppt에는 없는 여담", "Ppt 내용 추가", "막간 퀴즈")
_SUB = re.compile(r"^\s*(\(\d+\)|\d+\)|\d+\.|[①-⑩])\s")


def format_issues(note: LectureNote) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    body = [t for t in note.topics if t.role == "body" and not t.heading.upper().startswith("QUIZ")]
    if not body:
        return out
    if not (note.meta.get("points") or "").strip():
        out.append(("info", "POINTS_MISSING", "표지에 [강조점 세가지](meta.points)가 없습니다 — 교수님이 가장 강조한 것 2~4개를 목차 아래 상자로(L30)."))
    if not any(t.role == "closing" for t in note.topics):
        out.append(("info", "CLOSING_MISSING", "마무리 장 ‘Take home messages’(Topic.role=closing)가 없습니다 — 핵심 요약과 ★ 재강조로 닫습니다(L30)."))
    for t in note.topics:
        for sts in t.sections.values():
            for st in sts:
                if st.kind == "callout" and not any(st.left_title.startswith(x) for x in CALLOUT_TITLES):
                    out.append(("info", "CALLOUT_TITLE_UNKNOWN", f"'{t.heading}': 콜아웃 제목 ‘{st.left_title}’ — 기본 제목({' / '.join(CALLOUT_TITLES[:4])} …)을 씁니다(L33)."))
                if st.kind == "callout" and not st.left:
                    out.append(("warning", "CALLOUT_EMPTY", f"'{t.heading}': 콜아웃 ‘{st.left_title}’에 내용이 없습니다."))
                if st.kind == "sub" and not _SUB.search(st.text):
                    out.append(("info", "SUB_LINE_FORMAT", f"'{t.heading}': 소소제목 줄은 ‘(1) 제목 = 핵심’ 형태로 씁니다(L31): '{st.text[:24]}…'"))
    out += rhythm_issues(note) + emphasis_issues(note)
    return out


# ---- sentence rhythm (L38) and word emphasis (L35, L40)
_SENT = re.compile(r"(?<=[다요죠][.!?])\s+")
LONG_SENTENCE = 60


def _plain(s: str) -> str:
    from ..markup import strip

    return strip(s)


def rhythm_issues(note: LectureNote) -> list[tuple[str, str, str]]:
    """L38: sentences in paragraphs are short ones and explained ones; more than 30% over 60 characters = two facts in a sentence."""
    out: list[tuple[str, str, str]] = []
    allsent: list[tuple[str, str]] = []
    for t in note.topics:
        if t.role == "front":
            continue
        for sts in t.sections.values():
            for st in sts:
                if st.kind in ("para", "bullet") and st.origin != "author":
                    for x in _SENT.split(_plain(st.text)):
                        if len(x.strip()) >= 6:
                            allsent.append((t.heading, x.strip()))
    if len(allsent) >= 10:
        longs = [(h, x) for h, x in allsent if len(x) > LONG_SENTENCE]
        if len(longs) / len(allsent) > 0.30:
            h, x = max(longs, key=lambda a: len(a[1]))
            out.append(("warning", "SENTENCE_TOO_LONG",
                        f"61자를 넘는 문장이 {len(longs)}/{len(allsent)}개({len(longs) / len(allsent):.0%})입니다 → 사실 하나씩 둘로 나눕니다(L38). 가장 긴 문장: '{h}' {len(x)}자 '{x[:30]}…'"))
    return out


KEY_PER_TOPIC = 8


def emphasis_issues(note: LectureNote) -> list[tuple[str, str, str]]:
    """L40: red + 강조점 ({k|..}) is rationed; L35: a red whole sentence that only says '강조하셨습니다' is for exam scope, not for every emphasis."""
    from ..markup import runs

    out: list[tuple[str, str, str]] = []
    for t in note.topics:
        n = 0
        for sts in t.sections.values():
            for st in sts:
                n += sum(1 for _, c, _ in runs(st.text) if c == "key")
        if n > KEY_PER_TOPIC:
            out.append(("info", "KEY_EMPHASIS_TOO_MANY", f"'{t.heading}': 빨강+강조점 {{k|…}}이 {n}개입니다(소절당 {KEY_PER_TOPIC}개 이하) → 정말 외워야 할 단어만(L40)."))
    return out
