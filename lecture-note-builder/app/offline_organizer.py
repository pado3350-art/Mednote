"""Offline (no API) organizer: turns raw lecture paragraphs into readable study text with rules.

Honest scope: this is rule-based. It does NOT understand medicine - it cleans speech noise, converts spoken
endings to a study voice (한다체), highlights emphasis cues (red) and low-importance remarks (gray), bolds distinctive
English terms, builds 기본정석 boxes from the most salient sentences, writes 핵심 어휘 / 요약 정리 pages, and
marks sentences that match the PAD (blue). The result is a solid first draft; for the best quality let
Claude Code author the note with the `make-lecture-note` skill (still no API key needed).
"""
from __future__ import annotations

import math
import re
from collections import Counter

from .models import Slide, Statement, Topic
from .outline import _label
from .pad_match import PadMatcher

EMPH = ("중요", "반드시", "꼭 ", "꼭", "외워", "외우", "기억", "시험", "핵심", "특히", "강조", "국가시험", "구별", "구분", "혼동", "절대")
LOW = ("가볍게", "참고로", "굳이", "외울 필요는", "넘어가", "여담", "세부사항을 따라갈 필요는", "몰라도", "지엽")
META_END = re.compile(r"(보겠습니다|넘어가겠습니다|넘어갑니다|시작하겠습니다|살펴보겠습니다|알아보겠습니다|짚어 보겠습니다|말씀드리겠습니다|마치겠습니다)[.!]?$")
INSTR = re.compile(r"(그림|사진|표)을?\s*(한\s*번\s*더\s*)?(보|확인|찾아|살펴)")
LEAD = re.compile(r"^(자|그럼|그러면|이제|다음으로|먼저|그리고|그런데|그래서|그러니까|네)[,\s]+")
_EN = re.compile(r"(?<![A-Za-z0-9\-])([A-Za-z][A-Za-z0-9\-]{2,})(?![A-Za-z0-9\-])")
COMMON_EN = {"the", "and", "for", "that", "this", "with", "from", "class", "cell", "cells"}
DEF_PAT = re.compile(r"(이다|라고 한다|라고 부른다|뜻이다|의미한다|말한다|부른다)[.]?$")


# ------------------------------------------------------------------ style conversion
def _bnida(m: re.Match) -> str:
    ch = m.group(1)
    code = ord(ch) - 0xAC00
    if 0 <= code < 11172 and code % 28 == 17:  # final ㅂ -> ㄴ  (합니다 -> 한다, 갑니다 -> 간다)
        return chr(0xAC00 + code - 17 + 4) + "다"
    return m.group(0)


def to_study_voice(s: str) -> str:
    s = s.replace("아닙니다", "아니다").replace("입니다", "이다")
    s = re.sub(r"(겁니다|거예요|거에요)", "것이다", s)
    s = re.sub(r"([가-힣])시죠[?.!]?(?=\s|$)", r"\1자", s)  # "보시죠" -> "보자"
    s = re.sub(r"습니다", "다", s)
    s = re.sub(r"([가-힣])니다(?=[\s.!?,)]|$)", _bnida, s)
    s = re.sub(r"(이에요|예요)(?=[\s.!?]|$)", "이다", s)
    for a, b in (("있어요", "있다"), ("없어요", "없다"), ("같아요", "같다"), ("많아요", "많다"), ("좋아요", "좋다"),
                 ("해요", "한다"), ("돼요", "된다"), ("봐요", "본다")):
        s = re.sub(a + r"(?=[\s.!?]|$)", b, s)
    s = re.sub(r"(세요|십시오)(?=[\s.!?]|$)", "자", s)
    s = re.sub(r"(죠|지요)[?]?(?=[\s.!]|$)", "다", s)
    return s


def split_sentences(par: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[^\s])", par.strip())
    return [p.strip() for p in parts if p.strip()]


def _has_content(s: str) -> bool:
    return bool(re.search(r"\d", s) or _EN.search(s))


def clean_sentences(par: str) -> list[str]:
    out = []
    for s in split_sentences(par):
        t = LEAD.sub("", s).strip()
        if not t:
            continue
        if len(t) <= 60 and not _has_content(t) and (META_END.search(t) or INSTR.search(t) or re.fullmatch(r"[네그렇죠아시겠죠자,.?! ]+", t)):
            continue  # pure speech noise / pointer to a figure
        out.append(to_study_voice(t))
    return out


# ------------------------------------------------------------------ marking
def _emph(s: str) -> bool:
    return any(c in s for c in EMPH)


def _low(s: str) -> bool:
    return any(c in s for c in LOW)


def _bold_terms(sentences: list[str], seen: set[str], allowed: set[str]) -> list[str]:
    out = []
    for s in sentences:
        def rep(m: re.Match) -> str:
            t = m.group(1)
            k = t.lower()
            if k in seen or k not in allowed:
                return t
            seen.add(k)
            return f"**{t}**"
        out.append(_EN.sub(rep, s))
    return out


def _score(s: str) -> float:
    plain = re.sub(r"[{}*]|\b[rbgp]\|", "", s)
    sc = 2.0 * _emph(plain) + 1.0 * bool(_EN.search(plain)) + 0.7 * bool(re.search(r"\d", plain)) + 1.2 * bool(DEF_PAT.search(plain))
    sc -= 0.9 * _low(plain)
    sc -= max(0, len(plain) - 110) / 140.0
    return sc


# ------------------------------------------------------------------ section organizer
def term_allowlist(sections: list[list[Slide]]) -> list[set[str]]:
    """Per section: English terms distinctive enough to be bolded (not present in most sections)."""
    per = [Counter(m.group(1).lower() for u in sec for b in u.body for m in _EN.finditer(b.text)) for sec in sections]
    n = len(sections)
    df = Counter(k for c in per for k in c)
    cap = max(2, math.ceil(0.4 * n))
    return [{k for k in c if k not in COMMON_EN and df[k] <= cap and (len(k) >= 4 or "-" in k or any(ch.isdigit() for ch in k))}
            for c in per]


def organize_section(units: list[Slide], heading: str, chapter: str, allowed: set[str], matcher: PadMatcher | None) -> Topic:
    seen: set[str] = set()
    statements: list[Statement] = []
    cand: list[tuple[float, int, str, list[int]]] = []  # (score, order, sentence, refs) for the basics box
    all_pars = [b.text for u in units for b in u.body]
    order = 0
    for u in units:
        for b in u.body:
            sents = clean_sentences(b.text)
            if not sents:
                continue
            marked: list[str] = []
            refs = [u.number]
            pad_refs: set[int] = set()
            bolded = _bold_terms(sents, seen, allowed)
            for raw, s in zip(sents, bolded):
                pads = matcher.match(raw) if matcher else []
                order += 1
                cand.append((_score(raw), order, s, [u.number, *pads]))
                if pads:  # PAD content -> BLUE (and cite the PAD units)
                    pad_refs.update(pads)
                    marked.append("{b|" + s + "}")
                elif _low(raw):
                    marked.append("{g|" + s + "}")
                elif _emph(raw):
                    marked.append("{r|" + s + "}")
                else:
                    marked.append(s)
            title = _label([b.text], [x for x in all_pars]) if len(sents) > 1 else _label([b.text], all_pars)
            statements.append(Statement(text=title, kind="star", slide_refs=refs, origin="both"))
            statements.append(Statement(text=" ".join(marked), kind="para", slide_refs=refs + sorted(pad_refs),
                                        origin="lecturer"))
    top = sorted(cand, key=lambda c: (-c[0], c[1]))[:3]
    top = sorted(top, key=lambda c: c[1])
    basics, brefs = [], []
    for sc, _, s, refs in top:
        plain = s
        pads = [r for r in refs if r >= 1000]
        basics.append(("{b|" + plain + "}") if pads else plain)
        brefs += pads
    return Topic(heading=heading, chapter=chapter, slide_numbers=[u.number for u in units],
                 basics_title=heading, basics=basics, basics_refs=sorted(set(brefs)),
                 sections={"body": statements})


def _concept_map(body: list[Topic], key: str) -> list[Statement]:
    """Automatic schematic for 요약 정리: root + one card per chapter (or per section) with its key terms."""
    from .models import Diagram, Group

    if not body:
        return []

    def terms(t: Topic, k: int = 3) -> list[str]:
        out: list[str] = []
        for st in t.sections.get(key, []):
            for m in re.finditer(r"\*\*([^*]+)\*\*", st.text):
                if m.group(1) not in out:
                    out.append(m.group(1))
        return out[:k]

    palette = ["teal", "blue", "salmon", "amber", "violet", "green"]
    if any(t.chapter for t in body):
        chapters: dict[str, list[Topic]] = {}
        for t in body:
            chapters.setdefault(t.chapter or t.heading, []).append(t)
        groups = [Group(title=c, items=[f"§ {i}. {t.heading}" for i, t in enumerate(ts, 1)], color=palette[j % 6])
                  for j, (c, ts) in enumerate(chapters.items())]
    else:
        groups = []
        for j, t in enumerate(body[:6]):
            items = terms(t) or [re.sub(r"[{}*]|\b[rbgp]\|", "", t.basics[0])[:30]] if (terms(t) or t.basics) else []
            groups.append(Group(title=t.heading[:28], items=items, color=palette[j % 6]))
    spec = Diagram(kind="tree", title="핵심 개념 지도", root="이 강의의 구성", groups=groups)
    return [Statement(text="핵심 개념 지도 — 섹션별 핵심 용어", kind="diagram", diagram=spec, origin="both",
                      slide_refs=list(body[0].slide_numbers[:1]))]


def make_front_pages(topics: list[Topic], key: str) -> list[Topic]:
    """핵심 어휘 (distinctive terms with the sentence that defines them) + 요약 정리 (basics per section)."""
    body = [t for t in topics if t.role == "body"]
    # --- terms
    docs = []
    for t in body:
        sents = [(st, re.sub(r"\{[rbgp]\||\}|\*\*", "", st.text)) for st in t.sections.get(key, []) if st.kind == "para"]
        docs.append(sents)
    tf_sec: list[Counter] = [Counter(m.group(1) for _, txt in d for m in _EN.finditer(txt)) for d in docs]
    df = Counter(k.lower() for c in tf_sec for k in c)
    n = max(len(body), 1)
    best: dict[str, tuple[float, Statement, str]] = {}
    for c, d in zip(tf_sec, docs):
        for term, cnt in c.items():
            k = term.lower()
            if k in COMMON_EN or len(term) < 4 or df[k] > max(2, math.ceil(0.4 * n)):
                continue
            score = cnt * (math.log((n + 1) / (df[k] + 1)) + 1)
            for st, txt in d:
                for sent in split_sentences(txt):
                    if term in sent and (k not in best or score + (1.5 if DEF_PAT.search(sent) else 0) > best[k][0]):
                        best[k] = (score + (1.5 if DEF_PAT.search(sent) else 0), st, sent)
    chosen = sorted(best.items(), key=lambda kv: -kv[1][0])[:12]
    glossary = []
    for k, (_, st, sent) in chosen:
        term = next((m.group(1) for m in _EN.finditer(sent) if m.group(1).lower() == k), k)
        short = sent if len(sent) <= 120 else sent[:117].rstrip() + "…"
        blue = "{b|" in st.text
        text = f"**{term}** : {short}"
        glossary.append(Statement(text="{b|" + text + "}" if blue else text, kind="bullet",
                                  slide_refs=list(st.slide_refs), origin="both"))
    fronts = []
    if glossary:
        fronts.append(Topic(heading="핵심 어휘", role="front", slide_numbers=sorted({r for g in glossary for r in g.slide_refs if r < 1000}),
                            sections={key: [Statement(text="강의 전체에 나오는 핵심 용어를 먼저 훑어보자. 뒤에서 하나씩 다시 나온다.",
                                                      kind="para", slide_refs=glossary[0].slide_refs[:1], origin="both"), *glossary]}))
    summary = _concept_map(body, key)
    for t in body:
        if not t.basics:
            continue
        summary.append(Statement(text=t.heading, kind="star", slide_refs=t.slide_numbers[:1], origin="both"))
        for b in t.basics:
            refs = list(t.slide_numbers[:1]) + (list(t.basics_refs) if "{b|" in b else [])
            summary.append(Statement(text=b, kind="bullet", slide_refs=refs, origin="both"))
    if summary:
        fronts.append(Topic(heading="요약 정리", role="front", slide_numbers=sorted({r for s in summary for r in s.slide_refs if r < 1000}),
                            sections={key: summary}))
    return fronts
