"""Helpers for authoring a Topic-JSON note by hand (what Claude Code does in the API-free workflow).

Slides + script mode: `s=` are slide numbers (PPT p.N), `g=` are script paragraph ids (발화 ¶n), PAD units (>= 1000)
go into `s=` too. Nothing here knows about any particular lecture.
"""
from __future__ import annotations

import json

from app.models import Arrow, Diagram, Group, SlideTable, Statement, Topic  # noqa: F401  (re-exported for authors)


def _st(text, s, g, **kw):
    return Statement(text=text, slide_refs=list(s), segment_ids=list(g), origin="both", **kw)


def P(text, s=(), g=(), **kw):
    return _st(text, s, g, **kw)


def B(text, s=(), g=(), **kw):
    return _st(text, s, g, kind="bullet", **kw)


def STAR(text, s=(), g=()):
    return _st(text, s, g, kind="star")


def ADV(text, s=(), g=()):
    return _st(text, s, g, kind="advice")


def REF(text, s=(), g=()):
    return _st(text, s, g, kind="reference")


def QUIZ(stem, answer, options=(), s=(), g=()):
    return _st(stem, s, g, kind="quiz", options=list(options), answer=answer)


def DIA(spec: Diagram, caption: str, s=(), g=()):
    return _st(caption, s, g, kind="diagram", diagram=spec)


def slide_lines(slides, n: int, drop=(), maxlen: int = 400) -> list[str]:
    """Left column of a slide row: the slide's own lines (English original), '- ' bullets."""
    out = []
    for b in slides[n - 1].body:
        if any(d in b.text for d in drop):
            continue
        out.append("- " + (b.text if len(b.text) <= maxlen else b.text[: maxlen - 1].rstrip() + "…"))
    return out


def ROW(slides, n: int, right: str, g=(), drop=(), left=None, title=None, extra_s=()):
    """Two-column slide-table row: left = slide n (English original), right = explanation (Korean, '- ' bullets)."""
    return _st(right, [n, *extra_s], g, kind="row2",
               left_title=slides[n - 1].title if title is None else title,
               left=slide_lines(slides, n, drop) if left is None else list(left))


def TERM(term: str, definition: str, s=(), g=()):
    """Glossary row: term | definition."""
    return _st(definition, s, g, kind="row2", left_title=term, left=[])


def T(heading, chapter, slide_numbers, body, basics_title="", basics=(), tip="", tables=(), flags=(), role="body"):
    return Topic(heading=heading, chapter=chapter, role=role, slide_numbers=sorted(set(slide_numbers)),
                 basics_title=basics_title or heading, basics=list(basics), tip=tip,
                 sections={"body": body}, tables=list(tables), review_flags=list(flags))


def dump(topics, fp) -> None:
    json.dump({"topics": [t.model_dump() for t in topics]}, fp, ensure_ascii=False, indent=2)
