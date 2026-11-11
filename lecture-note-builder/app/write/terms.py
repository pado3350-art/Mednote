"""Uncommon Korean terms need English (approved rule L25): 핵군, 사이막핵, 뇌줄기 ... are textbook words nobody says in class or in notes.
Write the English term (septal nuclei, brainstem) or the English next to the Korean (사이막핵(septal nuclei) / septal nuclei(사이막핵)).

`RARE_KO` is a starter list; a lecture can add more with `meta.rare_terms` ("a|b|c"). Headings are checked strictly (English must be in the heading);
body statements pass when any English term of 3+ letters stands in the same statement.
"""
from __future__ import annotations

import re

from ..models import LectureNote

RARE_KO = {
    "핵군": "group (basolateral group)", "사이막핵": "septal nuclei", "사이막곁핵": "nucleus accumbens septi", "분계섬유줄": "stria terminalis",
    "뇌줄기": "brainstem", "후각계": "olfactory system", "겉질": "cortex", "속후각영역": "entorhinal cortex", "뇌활": "fornix",
    "해마형성체": "hippocampal formation", "편도핵": "amygdala", "가쪽뇌실": "lateral ventricle", "미상핵": "caudate nucleus",
}
_EN = re.compile(r"[A-Za-z]{3,}")


def _plain(s: str) -> str:
    return re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", s).replace("**", "")


def term_issues(note: LectureNote) -> list[tuple[str, str, str]]:
    terms = dict(RARE_KO)
    terms.update({x.strip(): "영어 용어" for x in (note.meta.get("rare_terms") or "").split("|") if x.strip()})
    out: list[tuple[str, str, str]] = []

    def hit(text: str, strict: bool) -> list[str]:
        t = _plain(text)
        found = [k for k in terms if k in t]
        if not found:
            return []
        if not strict and _EN.search(t):
            return []  # English stands in the same statement
        # strict (headings): the English must accompany the Korean term, e.g. 사이막핵(septal nuclei)
        return [k for k in found if not re.search(re.escape(k) + r"\s*[(（][A-Za-z]|[A-Za-z][A-Za-z ]*\s*[(（]" + re.escape(k), t)]

    seen = set()
    for t in note.topics:
        if t.role != "body":
            continue
        for label, text in (("장 제목", t.chapter), ("소절 제목", t.heading)):
            if text and text not in seen:
                seen.add(text)
                for k in hit(text, True):
                    out.append(("warning", "KOREAN_TERM_NO_ENGLISH", f"{label} '{text}': ‘{k}’은 잘 안 쓰는 한글 용어 → ‘{terms[k]}’처럼 영어로 쓰거나 병기(L25)."))
        for sts in t.sections.values():
            for st in sts:
                for line in [st.text, *st.left, *[c for r in st.rows for c in r]]:
                    for k in hit(line, False):
                        out.append(("warning", "KOREAN_TERM_NO_ENGLISH", f"'{t.heading}': ‘{k}’ → ‘{terms[k]}’ 영어로 쓰거나 병기(L25): '{_plain(line)[:26]}…'"))
    for b in [b for t in note.topics for b in t.basics]:
        for k in hit(b, False):
            out.append(("warning", "KOREAN_TERM_NO_ENGLISH", f"핵심 답 ‘{k}’ → ‘{terms[k]}’(L25): '{_plain(b)[:26]}…'"))
    return out
