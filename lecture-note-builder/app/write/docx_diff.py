"""Feedback learning, step 1: read two DOCX notes (AI original, user-edited) and list what changed.

Extraction (python-docx, document order):
  block = heading | paragraph | table cell paragraph, each with its runs' formatting (bold, colour, highlight)
Diff:
  modified / inserted / deleted / moved (order change) / format (same text, different bold or colour) /
  table_shape (rows or columns of a table changed)

Nothing here judges or applies anything - see app/write/feedback.py for classification and the approval gate.
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path
from typing import Literal, Optional

from docx import Document
from docx.oxml.ns import qn
from pydantic import BaseModel, Field

HEADING_MARKS = ("★", "§", "■", "▶")
_WS = re.compile(r"\s+")


class Span(BaseModel):
    text: str
    bold: bool = False
    color: str = ""  # RRGGBB, "" = default (black)
    highlight: str = ""


class Block(BaseModel):
    index: int  # position in document order
    kind: Literal["heading", "paragraph", "cell"]
    text: str
    spans: list[Span] = Field(default_factory=list)
    style: str = ""
    level: int = 0  # heading level (1 = chapter banner ...), 0 = not a heading
    table: Optional[int] = None  # cell: table number, row, column
    row: Optional[int] = None
    col: Optional[int] = None

    @property
    def where(self) -> str:
        if self.kind == "cell":
            return f"표 {self.table + 1} · {self.row + 1}행 {self.col + 1}열"
        return ("제목" if self.kind == "heading" else "문단") + f" #{self.index + 1}"


class TableShape(BaseModel):
    table: int
    rows: int
    cols: int
    first_cell: str = ""


class Extracted(BaseModel):
    path: str
    blocks: list[Block] = Field(default_factory=list)
    tables: list[TableShape] = Field(default_factory=list)


class Change(BaseModel):
    id: str
    type: Literal["modified", "inserted", "deleted", "moved", "format", "table_shape"]
    kind: str  # heading | paragraph | cell | table
    where: str
    before: str = ""
    after: str = ""
    removed: list[str] = Field(default_factory=list)  # word-level pieces taken out
    added: list[str] = Field(default_factory=list)  # word-level pieces put in
    bold_added: list[str] = Field(default_factory=list)
    bold_removed: list[str] = Field(default_factory=list)
    color_changes: list[str] = Field(default_factory=list)  # "텍스트: 색A→색B"
    from_index: Optional[int] = None
    to_index: Optional[int] = None
    similarity: float = 0.0
    # filled by app/write/feedback.py
    category: str = ""
    categories: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)


def norm(text: str) -> str:
    return _WS.sub(" ", text).strip()


# ------------------------------------------------------------------ extraction
def _run_props(r) -> tuple[bool, str, str]:
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        return False, "", ""
    b = rpr.find(qn("w:b"))
    bold = b is not None and b.get(qn("w:val"), "true") not in ("0", "false")
    c = rpr.find(qn("w:color"))
    color = (c.get(qn("w:val")) or "").upper() if c is not None else ""
    if color in ("AUTO", "000000"):
        color = ""
    h = rpr.find(qn("w:highlight"))
    return bold, color, (h.get(qn("w:val")) or "") if h is not None else ""


def _spans(p) -> list[Span]:
    out: list[Span] = []
    for r in p.iter(qn("w:r")):
        text = "".join(t.text or "" for t in r.iter(qn("w:t")))
        if not text:
            continue
        bold, color, hl = _run_props(r)
        if out and (out[-1].bold, out[-1].color, out[-1].highlight) == (bold, color, hl):
            out[-1].text += text  # merge runs that look the same
        else:
            out.append(Span(text=text, bold=bold, color=color, highlight=hl))
    return out


def _para_style(p) -> str:
    ppr = p.find(qn("w:pPr"))
    st = ppr.find(qn("w:pStyle")) if ppr is not None else None
    return st.get(qn("w:val")) or "" if st is not None else ""


def _is_shaded(p) -> bool:
    ppr = p.find(qn("w:pPr"))
    shd = ppr.find(qn("w:shd")) if ppr is not None else None
    return shd is not None and (shd.get(qn("w:fill")) or "").upper() not in ("", "AUTO", "FFFFFF")


def _heading_level(p, text: str, spans: list[Span], style: str) -> int:
    m = re.match(r"(?i)(heading|제목)\s*(\d)", style)
    if m:
        return int(m.group(2))
    if style.lower() == "title":
        return 1
    t = text.strip()
    if not t or len(t) > 80:
        return 0
    all_bold = bool(spans) and all(s.bold for s in spans if s.text.strip())
    if _is_shaded(p) and all_bold:  # MOM banners / § bands are shaded bold paragraphs
        return 2 if t.startswith("§") else 1
    if t.startswith(HEADING_MARKS) and all_bold:
        return 3
    return 0


def extract_docx(path: str | Path) -> Extracted:
    doc = Document(str(path))
    ex = Extracted(path=str(path))
    n_tables = 0

    def add(kind, p, **kw):
        spans = _spans(p)
        text = norm("".join(s.text for s in spans))
        if not text:
            return
        style = _para_style(p)
        level = _heading_level(p, text, spans, style) if kind != "cell" else 0
        ex.blocks.append(Block(index=len(ex.blocks), kind="heading" if level else kind, text=text, spans=spans,
                               style=style, level=level, **kw))

    for el in doc.element.body:
        tag = el.tag.split("}")[1]
        if tag == "p":
            add("paragraph", el)
        elif tag == "tbl":
            rows = el.findall(qn("w:tr"))
            n_cols = 0
            first = ""
            for ri, tr in enumerate(rows):
                cells = tr.findall(qn("w:tc"))
                n_cols = max(n_cols, len(cells))
                for ci, tc in enumerate(cells):
                    for p in tc.iter(qn("w:p")):
                        before = len(ex.blocks)
                        add("cell", p, table=n_tables, row=ri, col=ci)
                        if not first and len(ex.blocks) > before:
                            first = ex.blocks[-1].text[:40]
            ex.tables.append(TableShape(table=n_tables, rows=len(rows), cols=n_cols, first_cell=first))
            n_tables += 1
    return ex


# ------------------------------------------------------------------ diff
def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9\-]*|\d+(?:[.,]\d+)*%?|[가-힣]+|[^\sA-Za-z0-9가-힣]", text)


def word_diff(a: str, b: str) -> tuple[list[str], list[str]]:
    ta, tb = _tokens(a), _tokens(b)
    removed, added = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op in ("delete", "replace"):
            removed.append(" ".join(ta[i1:i2]))
        if op in ("insert", "replace"):
            added.append(" ".join(tb[j1:j2]))
    return removed, added


def _char_format(spans: list[Span]) -> list[tuple[str, bool, str]]:
    """Per non-space character: (char, bold, colour) - lets two runs with different run boundaries compare."""
    out = []
    for s in spans:
        for ch in s.text:
            if not ch.isspace():
                out.append((ch, s.bold, s.color or s.highlight))
    return out


def _segments(chars: list[str], flags: list[bool]) -> list[str]:
    out, cur = [], ""
    for ch, f in zip(chars, flags):
        if f:
            cur += ch
        elif cur:
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return out


def format_diff(a: Block, b: Block) -> tuple[list[str], list[str], list[str]]:
    """Bold / colour differences on the text the two blocks share (compared character by character)."""
    fa, fb = _char_format(a.spans), _char_format(b.spans)
    ca, cb = [x[0] for x in fa], [x[0] for x in fb]
    bold_add, bold_rem, colors = [], [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ca, cb, autojunk=False).get_opcodes():
        if op != "equal":
            continue
        chars = ca[i1:i2]
        pa, pb = fa[i1:i2], fb[j1:j2]
        bold_add += _segments(chars, [(not x[1]) and y[1] for x, y in zip(pa, pb)])
        bold_rem += _segments(chars, [x[1] and (not y[1]) for x, y in zip(pa, pb)])
        k = 0
        while k < len(chars):
            if pa[k][2] != pb[k][2]:
                j = k
                while j < len(chars) and (pa[j][2], pb[j][2]) == (pa[k][2], pb[k][2]):
                    j += 1
                colors.append(f"{''.join(chars[k:j])}: {pa[k][2] or '기본'}→{pb[k][2] or '기본'}")
                k = j
            else:
                k += 1
    return bold_add, bold_rem, colors


def _ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def diff_docs(orig: Extracted, edit: Extracted, pair_threshold: float = 0.5, move_threshold: float = 0.85) -> list[Change]:
    A, B = orig.blocks, edit.blocks
    ka, kb = [b.text for b in A], [b.text for b in B]
    pairs: list[tuple[Block, Block]] = []  # same or modified
    dels: list[Block] = []
    ins: list[Block] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ka, kb, autojunk=False).get_opcodes():
        if op == "equal":
            pairs += list(zip(A[i1:i2], B[j1:j2]))
            continue
        left, right = list(A[i1:i2]), list(B[j1:j2])
        if len(left) == 1 and len(right) == 1 and left[0].kind == right[0].kind and \
                (left[0].table, left[0].row, left[0].col) == (right[0].table, right[0].row, right[0].col):
            pairs.append((left[0], right[0]))  # one block rewritten in place, however heavily
            continue
        used: set[int] = set()
        last = -1
        for a in left:  # greedy, order-preserving pairing inside the changed stretch
            best, bj = pair_threshold, None
            for j in range(last + 1, len(right)):
                if j in used:
                    continue
                r = _ratio(a.text, right[j].text)
                if r > best:
                    best, bj = r, j
            if bj is None:
                dels.append(a)
            else:
                used.add(bj); last = bj
                pairs.append((a, right[bj]))
        ins += [b for j, b in enumerate(right) if j not in used]

    changes: list[Change] = []

    def new(**kw) -> Change:
        c = Change(id=f"C{len(changes) + 1}", **kw)
        changes.append(c)
        return c

    # moves: a deleted block that reappears (almost) unchanged elsewhere
    moved_ins: set[int] = set()
    still_deleted = []
    for a in dels:
        best, bb = move_threshold, None
        for b in ins:
            if b.index in moved_ins:
                continue
            r = _ratio(a.text, b.text)
            if r >= best:
                best, bb = r, b
        if bb is None:
            still_deleted.append(a)
            continue
        moved_ins.add(bb.index)
        c = new(type="moved", kind=bb.kind, where=f"{a.where} → {bb.where}", before=a.text, after=bb.text,
                from_index=a.index, to_index=bb.index, similarity=round(best, 3))
        if a.text != bb.text:
            c.removed, c.added = word_diff(a.text, bb.text)
    for a, b in sorted(pairs, key=lambda p: p[1].index):
        bold_add, bold_rem, colors = format_diff(a, b)
        fmt = bool(bold_add or bold_rem or colors)
        if a.text == b.text and a.kind == b.kind and not fmt:
            continue
        if a.text == b.text:
            new(type="format", kind=b.kind, where=b.where, before=a.text, after=b.text, bold_added=bold_add,
                bold_removed=bold_rem, color_changes=colors, similarity=1.0,
                from_index=a.index, to_index=b.index)
            continue
        removed, added = word_diff(a.text, b.text)
        new(type="modified", kind=b.kind if a.kind == b.kind else f"{a.kind}→{b.kind}", where=b.where, before=a.text,
            after=b.text, removed=removed, added=added, bold_added=bold_add, bold_removed=bold_rem,
            color_changes=colors, similarity=round(_ratio(a.text, b.text), 3), from_index=a.index, to_index=b.index)
    for a in still_deleted:
        new(type="deleted", kind=a.kind, where=a.where, before=a.text, from_index=a.index)
    for b in ins:
        if b.index not in moved_ins:
            new(type="inserted", kind=b.kind, where=b.where, after=b.text, to_index=b.index)

    # table shape
    for ta, tb in zip(orig.tables, edit.tables):
        if (ta.rows, ta.cols) != (tb.rows, tb.cols):
            new(type="table_shape", kind="table", where=f"표 {tb.table + 1} ({tb.first_cell})",
                before=f"{ta.rows}행 × {ta.cols}열", after=f"{tb.rows}행 × {tb.cols}열")
    if len(orig.tables) != len(edit.tables):
        new(type="table_shape", kind="table", where="문서 전체", before=f"표 {len(orig.tables)}개",
            after=f"표 {len(edit.tables)}개")
    changes.sort(key=lambda c: (c.to_index if c.to_index is not None else (c.from_index or 0)))
    for i, c in enumerate(changes, start=1):
        c.id = f"C{i}"
    return changes
