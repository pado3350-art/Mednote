"""Mixed (혼합형) note style - the DEFAULT body style (approved rule L10).

One lecture, two shapes:
  * explain § (개념·기전·원리·"왜"): question heading + one-line 핵심 답 box + short reasoning paragraphs
    (정의 → 그럼/왜 → 기전 사슬 → 따라서 한 줄 → 사례에 원리 적용).
  * list §    (수치·사례·제품·실험 결과·절차·분류): bullets / columns / tables, a one-line lead-in before a table
    and a "즉 …" line at the end.

`suggest_style` gives a first guess for a block of lecture text; `mixed_issues` checks a written note.
Learned from three human-written MOM notes (2025-08 신경계: 신경학적검사, 신경영상학, 혼미·혼수·뇌사):
docs/mixed_style_analysis.md.
"""
from __future__ import annotations

import re

from .models import LectureNote

# signals that a block explains a mechanism / reason / principle -> explain
EXPLAIN_CUES = re.compile(
    r"왜|때문|이유|원리|기전|메커니즘|mechanism|그래서|따라서|그러니까|결국|하면 .{0,8}된다|되면|그러면|"
    r"의미|개념|정의|라는 것은|이란|차이|달리|반면|역할|어떻게")
# signals that a block is data / cases / lists -> list
LIST_CUES = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:명|마리|개|원|억|만|년|월|개월|주|%|mg|ml|점|상)|p\s*[<=]|허가|승인|제품|회사|"
    r"첫째|둘째|셋째|①|②|③|종류|분류|목록|사례|케이스|임상시험|대조군|투여군|결과")

QUESTION_END = re.compile(r"(\?|까|나|가|는가|인가|일까|을까|ㄹ까)\s*$")
SUMMARY_START = re.compile(r"^\s*(?:\{[a-z]\|)?\s*(?:\*\*)?\s*(즉|따라서|결국|정리하면|요약하면)")


def style_scores(text: str) -> tuple[int, int]:
    """(explain score, list score) for a block of lecture text."""
    return len(EXPLAIN_CUES.findall(text)), len(LIST_CUES.findall(text))


def suggest_style(text: str) -> str:
    """'explain' or 'list' - a suggestion only; the writer decides with the lecture's logic in mind.

    List wins only when data clearly dominates (numbers/products/results at least 1.5x the reasoning cues),
    because a wrong 'list' loses the storyline while a wrong 'explain' only costs a few lines."""
    e, l = style_scores(text)
    return "list" if l >= max(3, 1.5 * e) else "explain"


def _plain(s: str) -> str:
    return re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", s).replace("**", "").strip()


def mixed_issues(note: LectureNote) -> list[tuple[str, str, str]]:
    """-> [(severity, code, message)] for a note written in the mixed style (template format.mixed)."""
    out: list[tuple[str, str, str]] = []
    body = [t for t in note.topics if t.role == "body" and not t.heading.upper().startswith("QUIZ")]
    styles = [t.style for t in body]
    for t in body:
        sts = [s for v in t.sections.values() for s in v]
        paras = [s for s in sts if s.kind == "para" and s.origin != "author"]
        bullets = [s for s in sts if s.kind == "bullet" and s.origin != "author"]
        texts = [_plain(s.text) for s in sts if s.kind in ("para", "bullet", "star")]
        if not t.style:
            out.append(("warning", "MIXED_STYLE_MISSING",
                        f"'{t.heading}': 혼합형에서는 소절마다 style(explain/list)을 정한다."))
            continue
        if t.style == "explain":
            if not t.basics:
                out.append(("warning", "EXPLAIN_NO_ANSWER", f"'{t.heading}': 설명형 소절은 한 줄 핵심 답(basics)으로 시작한다."))
            if len(bullets) > len(paras):
                out.append(("warning", "EXPLAIN_TOO_LISTY",
                            f"'{t.heading}': 설명형인데 bullet({len(bullets)})이 문단({len(paras)})보다 많다 → list로 바꾸거나 문단으로 잇는다."))
            if not QUESTION_END.search(_plain(t.heading)):
                out.append(("info", "EXPLAIN_HEADING_NOT_QUESTION", f"'{t.heading}': 설명형 제목은 질문으로 쓰면 흐름이 산다."))
        else:  # list
            if not any(SUMMARY_START.search(x) for x in texts):
                out.append(("warning", "LIST_NO_SUMMARY", f"'{t.heading}': 나열형 소절 끝에 '즉 …' 정리문 1줄을 쓴다(L2)."))
            long_paras = [s for s in paras if len(_plain(s.text)) > 160]
            if long_paras:
                out.append(("info", "LIST_LONG_PARAGRAPH",
                            f"'{t.heading}': 나열형인데 긴 문단 {len(long_paras)}개 → 수치·사례는 bullet/표로 나눈다."))
    if body and styles and all(s == styles[0] for s in styles) and styles[0]:
        out.append(("info", "MIXED_ONE_STYLE", f"모든 소절이 '{styles[0]}'이다. 혼합형은 개념은 설명형, 수치·사례는 나열형으로 나눈다."))
    return out
