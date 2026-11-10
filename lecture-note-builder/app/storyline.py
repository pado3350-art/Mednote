"""Top-down authoring: the storyline (`<out>/storyline.md`) is written BEFORE any note sentence.

`storyline_template` pre-fills what the program can see (skeleton cues in the lecture, PAD items, figures, paragraphs);
`storyline_issues` checks after the build that the note follows the storyline (STORYLINE_MISSING / STORYLINE_DRIFT).
Procedure and a worked example: .claude/skills/readable-note-organizer/references/top_down_storyline.md
"""
from __future__ import annotations

import re
from pathlib import Path

from .models import LectureNote

# phrases with which a lecturer announces the structure of the talk
SKELETON_CUES = re.compile(
    r"질문\s*\d|\d\s*번째\s*질문|첫\s*번째|두\s*번째|세\s*번째|네\s*번째|첫째|둘째|셋째|Part\s*\d|파트\s*\d|"
    r"\d\s*가지로\s*나뉩|크게\s*\d|정리하면|요약하면|결론적으로|목표는|할 수 있어야")


def skeleton_cues(segs) -> list[tuple[int, str]]:
    out = []
    for g in segs:
        if g.kind != "speech":
            continue
        for sent in re.split(r"(?<=[.?!])\s+", g.text):
            if SKELETON_CUES.search(sent):
                out.append((g.id, sent.strip()[:140]))
    return out


def storyline_template(segs, items=(), figs=(), title: str = "") -> str:
    cues = skeleton_cues(segs)
    speech = [g.id for g in segs if g.kind == "speech"]
    L = [f"# 스토리라인: {title or '<강의 제목>'}", "",
         "> 문장을 쓰기 전에 이 파일을 채워 `{out}/storyline.md`로 저장한다. 절차와 예시: "
         "`.claude/skills/readable-note-organizer/references/top_down_storyline.md`.", "",
         "## ① 강의의 뼈대 (강의 속 표현 그대로)",
         "아래는 프로그램이 찾은 구조 신호다. 강의가 스스로 가진 뼈대가 있으면 그것이 목차다.", ""]
    L += [f"- ¶{i}: “{s}”" for i, s in cues] or ["- (구조 신호 없음 — ②부터 직접 짠다)"]
    L += ["", "## ② 한 문장 요지", "", "## ③④⑤ 장과 소절",
          "### 1장 <제목> — 장 요지: ...", "",
          "| § | 질문 | 한 줄 답 | 모양(explain/list) | ¶ | 다음으로 가는 다리 |", "|---|---|---|---|---|---|", "| 1 |  |  |  |  |  |", "",
          f"모든 발화 단락이 정확히 한 소절에 들어가야 한다: ¶{speech[0]}–¶{speech[-1]} ({len(speech)}개)." if speech else "",
          "", "## ⑥ 반복되는 축", "- <개념>: 첫 등장 §x → 재등장 §y", "",
          "## ⑦ 시험 축 (앞쪽 요약은 이 표들 + 전체 지도 1장만)", "",
          "| PAD 유형 | 문항 | 답하는 § | 교수 언급 |", "|---|---|---|---|"]
    L += [f"|  | {it.label} (unit {it.number}): {it.question[:50]}… |  |  |" for it in items] or ["| (기출 없음) |  |  |  |"]
    L += ["", "## ⑧ 그림 인벤토리 (그림이 담은 사실 = 본문으로 옮길 내용)", "",
          "| 그림 | 담은 사실 | § |", "|---|---|---|"]
    L += [f"| {Path(f.path).name} |  |  |" for f in figs] or ["| (그림 없음) |  |  |"]
    L += ["", "## ⑨ 중요도", "- 강조: ", "- 읽고 넘김(effort: 참고): ", "- 생략(회색 메모 1줄): ", ""]
    return "\n".join(L)


def _norm(s: str) -> str:
    s = re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", s).replace("**", "")
    return re.sub(r"[\s\W_]+", "", s).lower()


def storyline_issues(note: LectureNote, path: str | Path) -> list[tuple[str, str, str]]:
    p = Path(path)
    if not p.exists():
        return [("warning", "STORYLINE_MISSING",
                 f"{p.name}가 없습니다. 문장을 쓰기 전에 스토리라인(뼈대 → 요지 → 장 → 소절의 질문과 한 줄 답 → 다리 → 시험 축 → 그림)을 먼저 씁니다.")]
    text = _norm(p.read_text(encoding="utf-8"))
    out = []
    for t in note.topics:
        if t.role != "body" or t.heading.upper().startswith("QUIZ"):
            continue
        if _norm(t.heading) not in text:
            out.append(("warning", "STORYLINE_DRIFT",
                        f"소절 '{t.heading}'이 스토리라인에 없습니다. 스토리라인을 고치거나 소절을 스토리라인에 맞춥니다."))
    return out


# ---- headings must say WHAT the lecture is about (subject + medical terms), not only "무엇을 고를까"
_GENERIC = sorted(["무엇", "어떻게", "어떤", "어디", "언제", "왜", "누구", "고를까", "줄까", "쓰나", "하나", "인가", "일까", "질문",
                   "원칙", "과정", "방법", "이유", "것", "장", "절"], key=len, reverse=True)
_PARTICLES = "은는이가을를에의로도와과"


def heading_content(heading: str) -> str:
    """The part of a heading that carries meaning: no digits, punctuation, question words or particles."""
    s = re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", heading).replace("**", "")
    s = re.sub(r"[\d\W_]+", "", s)
    for w in _GENERIC:
        s = s.replace(w, "")
    return "".join(c for c in s if c not in _PARTICLES)


def heading_issues(note: LectureNote, min_chars: int = 5, max_heading: int = 44, max_chapter: int = 34) -> list[tuple[str, str, str]]:
    """Chapter and § headings made only of question words ('질문1: 무엇을 고를까') tell the reader nothing."""
    out, seen = [], set()
    for t in note.topics:
        if t.role != "body" or t.heading.upper().startswith("QUIZ"):
            continue
        for label, text in (("장", t.chapter), ("소절", t.heading)):
            if text and text not in seen and len(heading_content(text)) < min_chars:
                seen.add(text)
                out.append(("warning", "HEADING_TOO_VAGUE",
                            f"{label} 제목 '{text}'에 주제와 의학 용어가 없습니다. 무엇에 대한 강의인지 제목만 읽어도 알 수 있게 "
                            "대상(예: 항균제)과 핵심 용어를 넣습니다. ‘질문N’은 본문 안 설명으로만 씁니다."))
            limit = max_chapter if label == "장" else max_heading
            if text and len(text) > limit and text not in seen:  # a heading that wraps to 2 lines is noise (the question box / table carry the detail)
                seen.add(text)
                out.append(("warning", "HEADING_TOO_LONG",
                            f"{label} 제목 '{text[:30]}…'이 {len(text)}자입니다(한 줄 {limit}자 이하). 세부 용어는 질문 상자와 표에 맡깁니다."))
    return out
