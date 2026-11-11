"""Top-down authoring: the storyline (`<out>/storyline.md`) is written BEFORE any note sentence.

`storyline_template` pre-fills what the program can see (skeleton cues in the lecture, PAD items, figures, paragraphs);
`storyline_issues` checks after the build that the note follows the storyline (STORYLINE_MISSING / STORYLINE_DRIFT).
Procedure and a worked example: .claude/skills/readable-note-organizer/references/top_down_storyline.md
"""
from __future__ import annotations

import re
from pathlib import Path

from ..models import LectureNote

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


def heading_issues(note: LectureNote, min_chars: int = 4, max_heading: int = 44, max_chapter: int = 34) -> list[tuple[str, str, str]]:
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


def keyword_heading_issues(note: LectureNote) -> list[tuple[str, str, str]]:
    """A chapter title that lists keywords after commas ('구조, 연결, fear') is not a title a reader can follow (approved rule L26):
    use a noun phrase in the lecture's own words ('편도체(amygdala)의 구조와 연결')."""
    out, seen = [], set()
    for t in note.topics:
        text = t.chapter
        if t.role == "body" and text and text not in seen and re.sub(r"\([^)]*\)", "", text).count(",") >= 2:
            seen.add(text)
            out.append(("info", "HEADING_KEYWORD_LIST", f"장 제목 '{text}'은 키워드를 쉼표로 나열했습니다. ‘~의 ~와 ~’ 명사구로, 강의 속 표현으로 씁니다(L26)."))
    return out


# ---- heading system of the human MOM (L27-L29): few sections, noun-phrase headings, the key line after " : "
_Q_END = re.compile(r"(\?|？|는가|인가|일까|을까|할까|[있없되하뉘르드]나)\s*\)?\s*$")  # real question endings only ("평가" is a noun)
_S_END = re.compile(r"[가-힣](다|요|니다|습니다|세요)\s*[.!]?\s*$")
MAX_SECTIONS = 12  # the human MOM (사시, 11쪽): 3 chapters, about 10 [n] sections
MAX_PER_CHAPTER = 6
LONG_MAX_SECTIONS, LONG_MAX_PER_CHAPTER, LONG_MAX_CHAPTERS = 20, 8, 6  # long lecture (docs/long_lecture.md)


def heading_form_issues(note: LectureNote, max_sections: int = MAX_SECTIONS, max_per_chapter: int = MAX_PER_CHAPTER) -> list[tuple[str, str, str]]:
    """§ headings are short noun phrases ('[2] 동공 반사', '[3] 사시 진단'), never questions or sentences; a lecture has about ten §.
    A question the lecturer actually asked goes into the body as a qa box, not into the heading."""
    out: list[tuple[str, str, str]] = []
    body = [t for t in note.topics if t.role == "body" and not t.heading.upper().startswith("QUIZ")]
    for t in body:
        h = re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", t.heading).replace("**", "").strip()
        if _Q_END.search(h):
            out.append(("warning", "HEADING_QUESTION", f"소절 제목 '{h}'이 질문형입니다 → 명사구로(예: ‘동공 반사의 경로’), 질문은 본문의 질문 상자로(L28)."))
        elif _S_END.search(h):
            out.append(("warning", "HEADING_SENTENCE", f"소절 제목 '{h}'이 문장형입니다 → 명사구로, 핵심 한 줄은 제목 뒤 ‘ : ’에(L28, L29)."))
        refs = {r for v in t.sections.values() for s in v for r in s.slide_refs if r < 1000}
        has_anchor = any(s.kind in ("rows", "figure", "diagram", "figure_side", "columns", "qa") for v in t.sections.values() for s in v)
        chars = sum(len(re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", x.text)) for v in t.sections.values() for x in v)
        if len(refs) <= 1 and not has_anchor and chars < 300:  # one long ¶ (many slides) written out in prose is not thin
            out.append(("info", "THIN_SECTION", f"소절 '{h}'은 발화 1개뿐이고 표·그림도 없습니다 → 앞뒤 소절과 합칩니다(L27)."))
    if str(note.meta.get("long_lecture") or "").lower() in ("true", "yes", "1"):  # docs/long_lecture.md
        max_sections, max_per_chapter = max(max_sections, LONG_MAX_SECTIONS), max(max_per_chapter, LONG_MAX_PER_CHAPTER)
        chapters = list(dict.fromkeys(t.chapter for t in body if t.chapter))
        if len(chapters) > LONG_MAX_CHAPTERS:
            out.append(("warning", "CHAPTER_TOO_MANY", f"장이 {len(chapters)}개입니다(긴 강의 한도 {LONG_MAX_CHAPTERS}) → 강의 자체의 목차 단위로 합칩니다."))
    if len(body) > max_sections:
        out.append(("warning", "SECTION_TOO_MANY", f"소절이 {len(body)}개입니다(한도 {max_sections}) → 같은 주제는 한 소절로 합치고, 세부 항목은 본문의 1. / (1) / ① 라벨 줄로(L27)."))
    per: dict[str, int] = {}
    for t in body:
        per[t.chapter] = per.get(t.chapter, 0) + 1
    for ch, k in per.items():
        if k > max_per_chapter:
            out.append(("warning", "SECTION_TOO_MANY", f"장 '{ch[:24]}'에 소절 {k}개(한도 {max_per_chapter}) → 합칩니다(L27)."))
    return out
