"""Anatomy needs a picture (anatomy-visual-explainer skill).

A § that talks about anatomical structures (nuclei, tracts, nerves, vessels, lobes ...) must show them: a slide figure first, a schematic otherwise.
`anatomy_issues` warns (ANATOMY_NO_VISUAL) for each such paragraph whose § has no figure / figure_side / diagram / concept picture.
It fires per paragraph, not per lecture: any paragraph (para, table, callout) that names 3+ distinct structures is an anatomy explanation,
whatever the lecture's main subject is. A lecture can add terms with `meta.anatomy_terms` ("a|b|c") or switch a § off with `meta.anatomy_text_only` ("§ heading|...").
"""
from __future__ import annotations

import re

from ..models import LectureNote, Topic

_KO = (
    "핵|신경|동맥|정맥|근육|인대|건|뇌실|뇌간|뇌줄기|대뇌|소뇌|겉질|피질|엽|이랑|고랑|회|열구|섬유|다발|경로|신경절|망울|막|공|구멍|관|굴|"
    "해마|편도체|시상|시상하부|뇌량|뇌활|중격|기저핵|망막|각막|수정체|맥락막|공막|홍채|시신경|시교차|외측슬상체|후두엽|안와|안구|"
    "척수|척추|늑골|흉골|쇄골|견갑|상완|요골|척골|대퇴|경골|비골|골반|두개골|천장골"
).split("|")
_KO_RX = re.compile("|".join(sorted((k for k in _KO if len(k) >= 2), key=len, reverse=True)))
_EN_RX = re.compile(
    r"\b(nucleus|nuclei|gyrus|gyri|sulcus|lobe|nerve|artery|vein|muscle|tract|fasciculus|ganglion|ganglia|cortex|ventricle|foramen|ligament|fossa|"
    r"plexus|cranial nerve|thalamus|hypothalamus|hippocampus|amygdala|cerebellum|brainstem|fornix|cingulate|retina|cornea|lens|optic|orbit|"
    r"vertebra|sinus|canal|duct|tendon|bone|septum|rectus|oblique|sphincter|levator|pons|midbrain|chiasm|radiation)\b|\bCN ?\d+\b", re.I)
_VISUAL = {"figure", "figure_side", "diagram"}


def _plain(s: str) -> str:
    return re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", s).replace("**", "")


def _topic_text(t: Topic) -> str:
    parts = [t.heading, *t.basics]
    for sts in t.sections.values():
        for st in sts:
            parts += [st.text, *st.left, *[c for r in st.rows for c in r]]
    return _plain(" ".join(parts))


def has_visual(t: Topic) -> bool:
    return any(st.kind in _VISUAL or (st.kind == "concept" and (st.image or st.diagram is not None)) for sts in t.sections.values() for st in sts)


def anatomy_terms_in(text: str, extra: set[str] | None = None) -> set[str]:
    found = {m.group(0) for m in _KO_RX.finditer(text)} | {(m.group(0) if m.group(0)[:2] == "CN" else m.group(0).lower()) for m in _EN_RX.finditer(text)}
    return found | {k for k in (extra or set()) if k and k in text}


def _statement_text(st) -> str:
    return _plain(" ".join([st.text, *st.left, *[c for r in st.rows for c in r]]))


def anatomy_paragraphs(t: Topic, min_terms: int = 3, extra: set[str] | None = None) -> list[tuple[object, set[str]]]:
    """Paragraphs (statements, tables, callouts) whose own content is an anatomy explanation: 3+ distinct structures named in it."""
    out = []
    for sts in t.sections.values():
        for st in sts:
            if st.kind in _VISUAL or st.kind == "concept":
                continue
            found = anatomy_terms_in(_statement_text(st), extra)
            if len(found) >= min_terms:
                out.append((st, found))
    return out


def anatomy_issues(note: LectureNote, min_terms: int = 3) -> list[tuple[str, str, str]]:
    """Per paragraph, not per lecture: a § gets a warning when one of its paragraphs explains anatomy and the § shows no picture."""
    extra = {x.strip() for x in (note.meta.get("anatomy_terms") or "").split("|") if x.strip()}
    off = {x.strip() for x in (note.meta.get("anatomy_text_only") or "").split("|") if x.strip()}
    out: list[tuple[str, str, str]] = []
    for t in note.topics:
        if t.role != "body" or t.heading in off or has_visual(t):
            continue
        paras = anatomy_paragraphs(t, min_terms, extra)
        if paras:
            refs = ", ".join(sorted({f"¶{st.slide_refs[0]}" for st, _ in paras if st.slide_refs}))
            found = set().union(*(f for _, f in paras))
            out.append(("warning", "ANATOMY_NO_VISUAL",
                        f"'{t.heading}' {refs}: 해부 구조({', '.join(sorted(found)[:6])})를 설명하는 문단이 있는데 소절에 그림이 없습니다. 강의자료 구조 그림(figure/figure_side)을 먼저, "
                        "없으면 도식(diagram)으로 위치·연결을 그립니다. 글만으로 충분하면 meta.anatomy_text_only에 소절 제목을 적습니다."))
    return out
