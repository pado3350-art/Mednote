"""AI-generated table of contents.

The lecture's overall flow (all paragraphs, in order) is sectioned into topics:
  * AnthropicOutliner  - Claude reads the whole script and proposes headings + ranges.
  * heuristic_outline  - offline fallback (topic-shift detection by lexical similarity).
Either result is normalised so every speech unit is covered exactly once, in order,
and note-kind units form a final appendix. The outline is saved as outline.json and can
be edited by hand and re-applied with --outline-json.
"""
from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from pathlib import Path

from .align_content import _bigrams, _cosine
from .models import Outline, OutlineItem, Slide

APPENDIX = "부록 & 검증 참고"
_TERM = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}")
_STOP = {"the", "and", "for", "that", "this", "with"}


def normalize_outline(outline: Outline, speech: list[int], notes: list[int]) -> Outline:
    """Cover every speech unit once, in order; unknown ids dropped; notes -> appendix."""
    valid = set(speech)
    seen: set[int] = set()
    items: list[OutlineItem] = []
    for it in outline.items:
        nums = [n for n in sorted(set(it.unit_numbers)) if n in valid and n not in seen]
        if nums:
            seen.update(nums)
            items.append(OutlineItem(heading=it.heading, unit_numbers=nums, summary=it.summary, chapter=it.chapter))
    for n in speech:  # anything the model skipped joins the nearest earlier section
        if n not in seen:
            if not items:
                items.append(OutlineItem(heading="강의 개요", unit_numbers=[]))
            prev = max((i for i, it in enumerate(items) if it.unit_numbers and it.unit_numbers[0] < n), default=0)
            items[prev].unit_numbers = sorted(items[prev].unit_numbers + [n])
            seen.add(n)
    if notes:
        items.append(OutlineItem(heading=APPENDIX, unit_numbers=list(notes)))
    return Outline(items=items)


def _label(paras: list[str], all_paras: list[str] | None = None) -> str:
    """Most distinctive terms of this chunk (tf-idf over paragraphs)."""
    all_paras = all_paras or paras
    N = len(all_paras)
    df = Counter(t.lower() for p in all_paras for t in set(_TERM.findall(p)))
    tf = Counter(t for p in paras for t in _TERM.findall(p) if t.lower() not in _STOP)
    scored = sorted(tf, key=lambda t: tf[t] * math.log((N + 1) / (1 + df[t.lower()])), reverse=True)
    top = []
    for t in scored:
        if t.lower() not in {x.lower() for x in top}:
            top.append(t)
        if len(top) == 2:
            break
    if top:
        return " · ".join(top)
    return re.split(r"[.!?。]", paras[0])[0][:24] if paras else "섹션"


def heuristic_outline(units: list[Slide], target: int | None = None) -> Outline:
    """Cut the paragraph sequence at the weakest lexical continuity points."""
    n = len(units)
    if n == 0:
        return Outline()
    k = target or max(2, min(10, round(n / 5)))
    k = min(k, n)
    vec = [_bigrams(u.plain_text()) for u in units]

    def win(lo, hi):
        c: Counter = Counter()
        for v in vec[max(lo, 0):min(hi, n)]:
            c.update(v)
        return c

    # similarity across each gap i|i+1 using 2-paragraph windows on both sides
    gaps = [(_cosine(win(i - 1, i + 1), win(i + 1, i + 3)), i) for i in range(n - 1)]
    cuts: list[int] = []
    for sim, i in sorted(gaps):  # weakest continuity first, keep sections >= 2 paragraphs
        if len(cuts) >= k - 1:
            break
        if all(abs(i - c) >= 2 for c in cuts) and i >= 1 and i <= n - 3:
            cuts.append(i)
    bounds = [0] + sorted(c + 1 for c in cuts) + [n]
    items = []
    for a, b in zip(bounds, bounds[1:]):
        chunk = units[a:b]
        items.append(OutlineItem(heading=_label([u.plain_text() for u in chunk], [u.plain_text() for u in units]),
                                 unit_numbers=[u.number for u in chunk]))
    return Outline(items=items)


OUTLINE_SYSTEM = """당신은 의과대학 강의록 편집자입니다. 번호가 붙은 강의 발화 단락 전체를 읽고, 강의의 전체적인 흐름을 판단해
학습용 강의록의 목차(섹션)를 만드세요.
- 시간 구간이나 기존 소제목에 얽매이지 말고 '주제 흐름'으로 나눈다.
- 2~4개의 챕터(chapter 제목, 번호 없이)로 묶고, 각 챕터 아래에 2~4개의 소절(heading)을 둔다. 소절마다 chapter 필드에 소속 챕터 제목을 같게 적는다.
- 각 섹션은 연속된 단락 번호 목록을 가지며, 모든 단락이 정확히 한 섹션에 속해야 한다.
- 제목은 간결한 한국어(필요한 영어 의학 용어 병기). 'I.' '§' 같은 번호는 붙이지 않는다.
- summary에는 그 섹션의 핵심 내용을 한 문장으로 적는다."""


class AnthropicOutliner:
    def __init__(self, client=None, model: str | None = None):
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self.client = client
        self.model = model or os.environ.get("MEDNOTE_MODEL", "claude-sonnet-5-5")

    def make_outline(self, units: list[Slide], pad_hint: list[str] | None = None) -> Outline:
        payload = {
            "paragraphs": [{"n": u.number, "text": u.plain_text()} for u in units],
            "exam_topics_hint": pad_hint or [],
        }
        schema = Outline.model_json_schema()
        tool = {"name": "emit_outline", "description": "Return the lecture table of contents.", "input_schema": schema}
        resp = self.client.messages.create(
            model=self.model, max_tokens=4000, system=OUTLINE_SYSTEM, tools=[tool],
            tool_choice={"type": "tool", "name": "emit_outline"},
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        )
        block = next(b for b in resp.content if getattr(b, "type", "") == "tool_use")
        return Outline.model_validate(block.input)


def save_outline(outline: Outline, path: str | Path) -> Path:
    p = Path(path)
    p.write_text(json.dumps(outline.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def load_outline(path: str | Path) -> Outline:
    return Outline.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
