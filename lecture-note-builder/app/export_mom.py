"""MOM-style layout, modelled on the reference notes (…MOM.pdf):

  cover: header box, big title banner, professor, 작성자 코멘트 (+ colour legend), 차례
         (chapters, "§" sections, dotted leader + page number)
  front pages: 핵심 어휘, 요약 정리
  body: every § starts a new page; each page repeats a teal chapter banner + "§ n. title";
        a 기본정석 box opens the §; Advice / Reference call-outs; colour-coded emphasis
  page number at the top-left of every page.

TOC page numbers are PAGEREF fields; `page_map` pre-fills their cached values so the file
looks right before Word refreshes fields (the pipeline fills it from a LibreOffice render).
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from .refs import format_refs
from .markup import runs, strip as _strip
from .models import LectureNote, Statement, Topic
from .template import Template

COLOR = {
    "emphasis": RGBColor(0xC0, 0x00, 0x00),
    "exam": RGBColor(0x1F, 0x4E, 0xC8),
    "exam_other": RGBColor(0x00, 0x96, 0xCD),  # 2nd blue: PAD of another professor (templates with `exam_other`)
    "minor": RGBColor(0x8C, 0x8C, 0x8C),
    "verify": RGBColor(0x70, 0x30, 0xA0),
}
BLACK = RGBColor(0, 0, 0)
GRAY_TAG = RGBColor(0x9A, 0x9A, 0x9A)
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]
_PREFIXED = re.compile(r"^\s*(\d+|[IVX]+)\.\s")
WEEKDAY = "월화수목금토일"


# ------------------------------------------------------------------ helpers
def _font(run, name: str, size: float | None = None, bold=None, color=None, italic=None, underline=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:eastAsia"), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if underline is not None:
        run.underline = underline
    if color is not None:
        run.font.color.rgb = color


def _run_style(run, col, F, size, bold=None, base_color=None):
    """Apply a markup colour tag: colours, 'highlight' (yellow marker) and 'underline'."""
    if col in ("highlight", "underline"):
        _font(run, F, size, bold=bold, color=base_color or BLACK)
        if col == "highlight":
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            run.underline = True
    else:
        _font(run, F, size, bold=bold, color=COLOR[col] if col else (base_color or BLACK))


def _fmt(p, before=0, after=6, line=1.3, left=None, first=None, align=None):
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
    if left is not None:
        pf.left_indent = Cm(left)
    if first is not None:
        pf.first_line_indent = Cm(first)
    if align is not None:
        p.alignment = align


def _box(cell, sz=12, color="000000", val="single"):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), val)
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:color"), color)
        b.append(e)
    tcPr.append(b)


def _field(p, instr: str, cached: str, font: str, size: float, bold=False, color=None):
    def r_el():
        r = p.add_run()
        _font(r, font, size, bold=bold, color=color)
        return r

    r = r_el(); fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "begin"); r._r.append(fc)
    r = r_el(); it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" {instr} "; r._r.append(it)
    r = r_el(); fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "separate"); r._r.append(fc)
    r = r_el(); r.text = cached
    r = r_el(); fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), "end"); r._r.append(fc)


def _bookmark(p, name: str, bid: int):
    s = OxmlElement("w:bookmarkStart"); s.set(qn("w:id"), str(bid)); s.set(qn("w:name"), name)
    e = OxmlElement("w:bookmarkEnd"); e.set(qn("w:id"), str(bid))
    p._p.insert(1 if p._p.pPr is not None else 0, s)
    p._p.append(e)


def numbering(note: LectureNote, roman: bool = False) -> list[dict]:
    """Per topic: chapter no/title and § no -> display strings (shared by TOC, banners, page lookup).
    roman=True: flat (chapter-less) topics get "I. / II. ..." starting at meta['numbering_start'] (default 1)."""
    out, ch_no, sec_no, last_ch, flat = [], 0, 0, None, int(note.meta.get("numbering_start", "1") or 1) - 1
    for t in note.topics:
        if t.role == "front":
            out.append({"front": True, "section": t.heading, "chapter": "", "banner": t.heading, "toc": None})
        elif t.chapter:
            if t.chapter != last_ch:
                ch_no += 1; sec_no = 0; last_ch = t.chapter
            sec_no += 1
            out.append({"front": False, "chapter": f"{ch_no}. {t.chapter}", "section": f"§ {sec_no}. {t.heading}",
                        "banner": f"{ch_no}. {t.chapter}", "toc": f"§ {sec_no}. {t.heading}", "no": sec_no})
        else:
            last_ch = None
            label = t.heading
            if roman and not _PREFIXED.match(t.heading) and t.heading != "부록 & 검증 참고":
                label = f"{ROMAN[flat % len(ROMAN)]}. {t.heading}"
                flat += 1
            out.append({"front": False, "chapter": "", "section": label, "banner": label, "toc": label, "no": 0})
    return out


def source_tag(st: Statement, note: LectureNote) -> str:
    return format_refs(st.slide_refs, note, st.time_ranges, st.segment_ids)


# --------------------------------------------------------------- statements
def _figure(doc, st: Statement, tpl: Template) -> None:
    """Centered picture + small gray caption. figure: <= 14 x 9 cm 'Figure n.'; diagram: full width '도식 n.';
    level 1 (summary page thumbnails): <= 9 x 5.5 cm '핵심 그림'."""
    from PIL import Image

    F = tpl.format.font_korean
    path = Path(st.image)
    if not path.exists():
        return
    with Image.open(path) as im:
        w, h = im.size
    if st.kind == "diagram":
        doc._dia_n = getattr(doc, "_dia_n", 0) + 1
        label, width_cm = f"도식 {doc._dia_n}.", min(16.8, 11.0 * w / max(h, 1))
    elif st.level >= 1:
        label, width_cm = "핵심 그림.", min(9.0, 5.5 * w / max(h, 1))
    else:
        doc._fig_n = getattr(doc, "_fig_n", 0) + 1
        label, width_cm = f"그림 {doc._fig_n}.", min(14.0, 9.0 * w / max(h, 1))
    p = doc.add_paragraph()
    _fmt(p, before=6, after=2, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    c = doc.add_paragraph()
    _fmt(c, after=8, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = c.add_run(f"{label} {_strip(st.text)}")
    _font(r, F, 8.5, color=COLOR["minor"])


def _statement(doc, st: Statement, note: LectureNote, tpl: Template):
    if st.kind in ("figure", "diagram"):
        _figure(doc, st, tpl)
        return
    if st.kind == "figure_side":
        _figure_side(doc, st, tpl)
        return
    if st.kind == "columns":
        _columns_box(doc, st, tpl)
        return
    F = tpl.format.font_korean
    base = tpl.format.font_size_pt
    p = doc.add_paragraph()
    base_color = COLOR["emphasis"] if st.emphasis else COLOR.get(st.tag, BLACK)
    base_bold = st.emphasis or None
    ind = 0.6 * st.level
    if st.kind in ("advice", "reference"):
        _fmt(p, before=6, after=6, line=1.3, left=2.2 + ind, first=-2.2)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(2.2))
        r = p.add_run(("Advice" if st.kind == "advice" else "Reference") + "\t")
        _font(r, F, base + 1, bold=True, italic=True, color=COLOR["emphasis"])
        size = base
    elif st.kind == "star":
        p.paragraph_format.keep_with_next = True  # never leave a sub-heading alone at the bottom of a page
        if tpl.format.star_style == "band":  # light-blue band like the clinical notes' sub-heading rows
            _fmt(p, before=10, after=5, line=1.2, left=0.1 + ind)
            _shade_par(p, "DCE9F7")
        else:
            _fmt(p, before=10, after=6, line=1.25, left=0.9 + ind)
            r = p.add_run("★ "); _font(r, F, base + 0.5, bold=True)
        size, base_bold = base + 0.5, True
    elif st.kind == "bullet":
        _fmt(p, after=3, line=1.25, left=1.5 + ind, first=-0.45)
        r = p.add_run("-  "); _font(r, F, base - 0.5)
        size = base - 0.5
    else:
        _fmt(p, after=6, line=1.35, left=ind)
        size = base
    for text, col, bold in runs(st.text):
        r = p.add_run(text)
        _run_style(r, col, F, size, bold=True if (bold or base_bold) else None, base_color=base_color)
    if tpl.format.include_source_references and st.kind == "para":
        tag = source_tag(st, note)
        if tag:
            r = p.add_run(f"  [{tag}]")
            _font(r, F, 7, color=GRAY_TAG)


def _cell_fill(cell, fill: str) -> None:
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(sh)


def _figure_side(doc, st: Statement, tpl: Template) -> None:
    """One bordered box: picture (+ 'Figure n.' caption) on the left, title + bullet lines on the right.
    Saves about half the height of a full-width figure followed by text (MOM handout layout)."""
    from PIL import Image

    F, base = tpl.format.font_korean, tpl.format.font_size_pt
    path = Path(st.image) if st.image else None
    has_pic = path is not None and path.exists()
    t = doc.add_table(rows=1, cols=2 if has_pic else 1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    pic_w = 7.2
    if has_pic:
        with Image.open(path) as im:
            w, h = im.size
        pic_w = min(7.2, 8.5 * w / max(h, 1))  # tall pictures get narrower
        widths = (pic_w + 0.4, 17.4 - pic_w - 0.4)
        for ci, wd in enumerate(widths):
            t.columns[ci].width = Cm(wd)
            t.rows[0].cells[ci].width = Cm(wd)
        c0 = t.cell(0, 0)
        p = c0.paragraphs[0]; _fmt(p, before=3, after=1, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.add_run().add_picture(str(path), width=Cm(pic_w))
        doc._fig_n = getattr(doc, "_fig_n", 0) + 1
        q = c0.add_paragraph(); _fmt(q, after=2, line=1.05, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = q.add_run(f"그림 {doc._fig_n}. {_strip(st.text)}"); _font(r, F, 7.5, color=COLOR["minor"])
    tc = t.cell(0, 1 if has_pic else 0)
    first = tc.paragraphs[0]
    if st.left_title:
        _fmt(first, before=3, after=3, line=1.15)
        for text, col, bold in runs(st.left_title):
            r = first.add_run(text); _run_style(r, col, F, base + 0.5, bold=True)
        first = None
    _lines_into(tc, list(st.left), F, base - 0.5, tpl, first_par=first, bullet="-", tight=True)
    for row in t.rows:
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); row._tr.get_or_add_trPr().append(cs)
    _fmt(doc.add_paragraph(), after=3, line=0.8)


def _columns_box(doc, st: Statement, tpl: Template) -> None:
    """Parallel items side by side (e.g. UK Biobank | All of Us | 국가 사업): one column per diagram group."""
    from .diagrams import CYCLE, PALETTE

    F, base = tpl.format.font_korean, tpl.format.font_size_pt
    groups = st.diagram.groups if st.diagram is not None else []
    if not groups:
        return
    if st.text:
        p = doc.add_paragraph(); _fmt(p, before=4, after=3, line=1.15)
        p.paragraph_format.keep_with_next = True
        for text, col, bold in runs(st.text):
            r = p.add_run(text); _run_style(r, col, F, base + 0.5, bold=True)
    t = doc.add_table(rows=2, cols=len(groups))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    w = 17.4 / len(groups)
    for ci, g in enumerate(groups):
        for ri in range(2):
            t.rows[ri].cells[ci].width = Cm(w)
        rgb = PALETTE.get(g.color or CYCLE[ci % len(CYCLE)], PALETTE["teal"])
        hc = t.cell(0, ci); _cell_fill(hc, "%02X%02X%02X" % rgb)
        hp = hc.paragraphs[0]; _fmt(hp, before=2, after=2, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER)
        hp.paragraph_format.keep_with_next = True
        for text, col, bold in runs(g.title):
            r = hp.add_run(text); _font(r, F, base, bold=True, color=RGBColor(255, 255, 255))
        bc = t.cell(1, ci)
        _lines_into(bc, [x if x.startswith("- ") else "- " + x for x in g.items], F, base - 0.5, tpl,
                    first_par=bc.paragraphs[0], bullet="-", tight=True)
    for row in t.rows:
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); row._tr.get_or_add_trPr().append(cs)
    _fmt(doc.add_paragraph(), after=3, line=0.8)


def _section_heading(doc, label: str, F: str, base: float, idx: int) -> None:
    """In-flow § heading used when topics do not start a new page (page_break: chapter)."""
    p = doc.add_paragraph()
    _fmt(p, before=10, after=5, line=1.15, left=0.0)
    p.paragraph_format.keep_with_next = True
    _shade_par(p, "DCEFEA")
    r = p.add_run(" " + label); _font(r, F, base + 2.5, bold=True, color=RGBColor(0x1F, 0x5F, 0x55))
    _bookmark(p, f"_Toc{idx}", idx + 1)


def _table(doc, tb, tpl: Template):
    F = tpl.format.font_korean
    _fmt(doc.add_paragraph(), after=2)
    ncol = max(len(r) for r in tb.rows)
    t = doc.add_table(rows=len(tb.rows), cols=ncol)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    if tb.col_widths_cm and len(tb.col_widths_cm) == ncol:
        t.autofit = False
        for ci, w in enumerate(tb.col_widths_cm):
            t.columns[ci].width = Cm(w)
            for row in t.rows:
                row.cells[ci].width = Cm(w)
    trPr = t.rows[0]._tr.get_or_add_trPr()  # repeat header row on page breaks
    hdr = OxmlElement("w:tblHeader"); hdr.set(qn("w:val"), "true"); trPr.append(hdr)
    for row in t.rows:  # never split a row across pages
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); row._tr.get_or_add_trPr().append(cs)
    def heat(ci, ri):
        try:
            v = float(tb.rows[ri][ci])
        except (ValueError, IndexError):
            return None
        mx = max((float(r[ci]) for r in tb.rows[1:] if len(r) > ci and r[ci].replace(".", "", 1).isdigit()), default=0) or 1
        k = min(max(v / mx, 0.0), 1.0)
        # white -> red like the reference heat table (0 -> light green for "none")
        if v == 0:
            return "7BC47F"
        r, g, b = 255, int(255 - 175 * k), int(255 - 190 * k)
        return f"{r:02X}{g:02X}{b:02X}"

    for ri, row in enumerate(tb.rows):
        for ci in range(ncol):
            c = t.cell(ri, ci)
            c.text = ""
            p = c.paragraphs[0]
            _fmt(p, after=1, line=1.15)
            if ri < 2:
                p.paragraph_format.keep_with_next = True
            for text, col, bold in runs(row[ci] if ci < len(row) else ""):
                r = p.add_run(text)
                _run_style(r, col, F, tpl.format.font_size_pt - 1, bold=True if (bold or ri == 0 or ci == 0) else None)
            if ri > 0 and ci in tb.heat_cols and (fill := heat(ci, ri)):
                sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), fill)
                c._tc.get_or_add_tcPr().append(sh)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if ri == 0:
                sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), "EDEDED")
                c._tc.get_or_add_tcPr().append(sh)
    if tb.caption:
        p = doc.add_paragraph()
        _fmt(p, before=3, after=8)
        r = p.add_run(tb.caption); _font(r, F, 8.5, color=COLOR["minor"])
    else:
        _fmt(doc.add_paragraph(), after=4)


# ------------------------------------------------------------------ pieces
TEAL = "8FBFB8"
TEAL_DARK = "1F8A7A"
SALMON = "FF5C66"


def _shade_par(p, fill: str):
    pPr = p._p.get_or_add_pPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), fill)
    pPr.append(sh)


def _shade_run(r, fill: str):
    rPr = r._element.get_or_add_rPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), fill)
    rPr.append(sh)


def _banner(container, text: str, F: str, fill=TEAL_DARK, size=20, color=RGBColor(255, 255, 255), before=0, after=4):
    p = container.add_paragraph()
    _fmt(p, before=before, after=after, line=1.1, left=2.4, align=WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.right_indent = Cm(2.4)
    _shade_par(p, fill)
    r = p.add_run(text); _font(r, F, size, bold=True, color=color)
    return p


def _page_header(header, note_text: str | None, banner: str | None, section: str | None, F: str, tpl: Template):
    header.is_linked_to_previous = False
    for p in list(header.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    hp = header.paragraphs[0]
    for r in list(hp.runs):
        r._r.getparent().remove(r._r)
    _fmt(hp, after=2, line=1.0)
    _field(hp, "PAGE", "1", F, 9)
    if banner:
        _banner(header, banner, F)
    if section:
        p = header.add_paragraph(); _fmt(p, before=2, after=6, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(section); _font(r, F, 15, bold=False)


def _basics_box(doc, t: Topic, n: int, F: str, base: float):
    box = doc.add_table(rows=1, cols=1)
    box.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = box.cell(0, 0)
    tcPr = c._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side, sz, col in (("top", 18, "C00000"), ("bottom", 18, "C00000"), ("left", 0, "FFFFFF"), ("right", 0, "FFFFFF")):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single" if sz else "nil"); e.set(qn("w:sz"), str(sz or 0)); e.set(qn("w:color"), col)
        b.append(e)
    tcPr.append(b)
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), "F2F2F2"); tcPr.append(sh)
    p = c.paragraphs[0]; _fmt(p, before=4, after=4, line=1.2)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(17.0), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(f" {n} "); _font(r, F, base, bold=True); r.font.color.rgb = BLACK
    r = p.add_run("  " + (t.basics_title or t.heading)); _font(r, F, base + 1, bold=True)
    r = p.add_run("\t"); _font(r, F, base)
    r = p.add_run(" 기본정석 "); _font(r, F, base - 1, bold=True, color=RGBColor(255, 255, 255)); _shade_run(r, "D9242B")
    for i, line in enumerate(t.basics, start=1):
        q = c.add_paragraph(); _fmt(q, after=2, line=1.25, left=1.5, first=-0.7)
        r = q.add_run(f"{i})  "); _font(r, F, base + 0.5)
        for text, col, bold in runs(line):
            r = q.add_run(text)
            _run_style(r, col, F, base + 0.5, bold=True if bold else None)
    _fmt(c.add_paragraph(), after=0, line=0.6)
    _fmt(doc.add_paragraph(), after=4)


def _lines_into(cell_or_doc, text_lines: list[str], F: str, size: float, tpl: Template, first_par=None, bullet="●", tight=False):
    """Write markup lines into a cell (or document). A leading '- ' makes a hanging bullet."""
    first = True
    for line in text_lines:
        p = first_par if (first and first_par is not None) else cell_or_doc.add_paragraph()
        first = False
        bul = line.startswith("- ")
        body = line[2:] if bul else line
        _fmt(p, after=2 if tight else 3, line=1.25, left=0.55 if bul else 0.0, first=-0.55 if bul else None)
        if bul:
            r = p.add_run(f"{bullet}  "); _font(r, F, size - 1)
        for text, col, bold in runs(body):
            r = p.add_run(text)
            _run_style(r, col, F, size, bold=True if bold else None)


def _row2_table(doc, rows: list[Statement], tpl: Template) -> None:
    """Two-column 'slide table': left = slide / English original (+ picture), right = explanation (Korean)."""
    from PIL import Image

    F = tpl.format.font_korean
    base = tpl.format.font_size_pt
    t = doc.add_table(rows=len(rows), cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    glossary = all(not r.left and not r.image for r in rows)  # term | explanation rows -> narrow left column
    widths = (5.0, 12.4) if glossary else (8.2, 9.2)
    for ci, w in enumerate(widths):
        t.columns[ci].width = Cm(w)
    for ri, st in enumerate(rows):
        lc, rc = t.cell(ri, 0), t.cell(ri, 1)
        lc.width, rc.width = Cm(widths[0]), Cm(widths[1])
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); t.rows[ri]._tr.get_or_add_trPr().append(cs)
        lp = lc.paragraphs[0]
        if st.left_title:
            _fmt(lp, after=3, line=1.2)
            r = lp.add_run(st.left_title); _font(r, F, base, bold=True)
            _lines_into(lc, st.left, F, base - 0.5, tpl, tight=True)
        else:
            _lines_into(lc, st.left or [""], F, base - 0.5, tpl, first_par=lp, tight=True)
        if st.image and Path(st.image).exists():
            with Image.open(st.image) as im:
                w, h = im.size
            ip = lc.add_paragraph(); _fmt(ip, before=4, after=2, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
            ip.add_run().add_picture(st.image, width=Cm(min(7.4, 5.2 * w / max(h, 1))))
        _lines_into(rc, [ln for ln in st.text.split("\n")], F, base, tpl, first_par=rc.paragraphs[0])
    _fmt(doc.add_paragraph(), after=4, line=0.8)


def _quiz_box(doc, st: Statement, tpl: Template) -> None:
    """QUIZ n box (case / stem in bold + options) followed by the answer line."""
    F = tpl.format.font_korean
    base = tpl.format.font_size_pt
    doc._quiz_n = getattr(doc, "_quiz_n", 0) + 1
    box = doc.add_table(rows=1, cols=1)
    box.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = box.cell(0, 0)
    _box(c, sz=8)
    p = c.paragraphs[0]; _fmt(p, before=3, after=4, line=1.3)
    r = p.add_run(f"QUIZ {doc._quiz_n}.  "); _font(r, F, base, bold=True)
    for text, col, bold in runs(st.text):
        r = p.add_run(text); _run_style(r, col, F, base, bold=True)
    for i, o in enumerate(st.options, start=1):
        q = c.add_paragraph(); _fmt(q, after=1, line=1.2, left=1.0, first=-0.6)
        label = "" if re.match(r"^\s*(\d+[.)]|[①-⑤])", o) else f"{i}. "
        for text, col, bold in runs(label + o):
            r = q.add_run(text); _run_style(r, col, F, base - 0.5, bold=True)
    _fmt(c.add_paragraph(), after=0, line=0.5)
    if st.answer:
        a = doc.add_paragraph(); _fmt(a, before=4, after=6, line=1.3, left=0.2)
        r = a.add_run("→ 정답: "); _font(r, F, base, bold=True, color=COLOR["emphasis"])
        for text, col, bold in runs(st.answer):
            r = a.add_run(text); _run_style(r, col, F, base, bold=True)


def _tip_line(doc, t: Topic, F: str, base: float) -> None:
    p = doc.add_paragraph(); _fmt(p, before=2, after=8, line=1.3, left=0.2)
    r = p.add_run("공부 팁  "); _font(r, F, base - 0.5, bold=True, color=COLOR["emphasis"])
    for text, col, bold in runs(t.tip):
        r = p.add_run(text); _run_style(r, col or "highlight", F, base - 0.5, bold=True if bold else None)


# ------------------------------------------------------------------- export
def _used_tags(note: LectureNote) -> set[str]:
    used = {s.tag for t in note.topics for sts in t.sections.values() for s in sts}
    from .markup import COLORS

    def scan(text: str) -> None:
        for m in re.finditer(r"\{([rbgpcyu])\|", text):
            used.add(COLORS[m.group(1)])

    for t in note.topics:
        for sts in t.sections.values():
            for s in sts:
                if s.emphasis:
                    used.add("emphasis")
                for x in (s.text, *s.left, *s.options, s.answer):
                    scan(x)
        for line in (*t.basics, t.tip):
            scan(line)
    return used


def _legend_lines(container, note: LectureNote, tpl: Template, F: str, stacked: bool) -> None:
    used = _used_tags(note)
    legend = [i for i in tpl.format.legend if i.tag in used]
    if not legend:
        return
    if stacked:  # one line per colour, like the clinical notes' comment box
        for item in legend:
            p = container.add_paragraph(); _fmt(p, after=2, line=1.2, left=1.6)
            r = p.add_run(item.word); _run_style(r, item.tag if item.tag != "emphasis" else "emphasis", F, 8.5, bold=True)
            r = p.add_run(f" : {item.meaning}"); _font(r, F, 8.5)
    else:
        p = container.add_paragraph(); _fmt(p, before=2, after=4, left=0.2)
        for k, item in enumerate(legend):
            r = p.add_run(("    " if k else "") + item.word); _run_style(r, item.tag, F, 8.5, bold=True)
            r = p.add_run(f" : {item.meaning}"); _font(r, F, 8.5)


def _tips(container, note: LectureNote, F: str, size: float = 9) -> None:
    """meta['tips'] (newline separated): the author's study strategy, yellow-highlighted."""
    for line in (note.meta.get("tips") or "").split("\n"):
        if line.strip():
            p = container.add_paragraph(); _fmt(p, before=1, after=3, line=1.3, left=0.2)
            for text, col, bold in runs(line):
                r = p.add_run(text); _run_style(r, col or "highlight", F, size, bold=True if bold else None)


def export_mom(
    note: LectureNote, tpl: Template, out_path: str | Path, page_map: dict[int, int] | None = None
) -> Path:
    F = tpl.format.font_korean
    base = tpl.format.font_size_pt
    page_map = page_map or {}
    nums = numbering(note, tpl.format.roman_headings)
    doc = Document()
    for name in ("Normal", "Table Grid"):
        st = doc.styles[name]
        st.font.name = F
        st.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), F)
    doc.styles["Normal"].font.size = Pt(base)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin, sec.bottom_margin = Cm(1.6), Cm(1.6)
    sec.header_distance = Cm(0.9)
    text_width = 21.0 - 3.6
    meta = note.meta
    box_cover = tpl.format.cover_style == "box"
    n_cover_lines = len([x for x in (meta.get("tips") or "").split("\n") if x.strip()]) + \
        len([x for x in (meta.get("objectives") or "").split("\n") if x.strip()])
    dense = n_cover_lines >= 6 or len(meta.get("comment", "")) > 520  # keep the cover on ONE page

    # ---------------- cover: title box (double line in the "box" cover)
    _page_header(sec.header, None, None, None, F, tpl)
    box = doc.add_table(rows=1, cols=1)
    box.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = box.cell(0, 0)
    _box(cell, sz=18 if box_cover else 24, val="double" if box_cover else "single")
    date_line = ""
    if meta.get("date"):
        d = dt.date.fromisoformat(meta["date"])
        date_line = f"{d.year}년 {d.month}월 {d.day}일 {WEEKDAY[d.weekday()]}요일"
    if meta.get("period"):
        date_line += f" {meta['period']}"
    if meta.get("subject"):
        date_line += f" <{meta['subject']}>"
    if meta.get("professor"):
        date_line += f" {meta['professor']} 교수님"
    p = cell.paragraphs[0]; _fmt(p, before=6, after=2)
    r = p.add_run(date_line); _font(r, F, 9.5)
    p = cell.add_paragraph(); _fmt(p, before=4 if box_cover else 2, after=6 if box_cover else 4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run(note.title); _font(r, F, 22 if box_cover else 20, bold=True)
    p = cell.add_paragraph(); _fmt(p, after=6, align=WD_ALIGN_PARAGRAPH.RIGHT)
    r = p.add_run(meta.get("author", "")); _font(r, F, 9.5)

    if not box_cover:  # big colour banner cover
        if meta.get("edition"):
            p = doc.add_paragraph(); _fmt(p, before=14, after=2, align=WD_ALIGN_PARAGRAPH.RIGHT)
            r = p.add_run(meta["edition"]); _font(r, F, 14, bold=True, color=RGBColor(0xFF, 0x4B, 0x2B))
        if meta.get("series"):
            _banner(doc, "", F, fill=SALMON, size=6, before=2, after=0).paragraph_format.left_indent = Cm(0)
            p = doc.add_paragraph(); _fmt(p, before=8, after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
            r = p.add_run(meta["series"]); _font(r, F, 40, bold=True)
        tb = _banner(doc, note.title, F, fill=SALMON, size=19 if dense else 24, before=6 if dense else 10, after=0)
        tb.paragraph_format.left_indent = Cm(0); tb.paragraph_format.right_indent = Cm(0)
        tb.paragraph_format.space_before = Pt(6 if dense else 10)
        if meta.get("professor"):
            p = doc.add_paragraph(); _fmt(p, before=4 if dense else 10, after=3 if dense else 8, align=WD_ALIGN_PARAGRAPH.CENTER)
            r = p.add_run(meta["professor"]); _font(r, F, 17 if dense else 24, bold=True)
            r = p.add_run(" 교수님"); _font(r, F, 12 if dense else 14, bold=True)
    else:
        _fmt(doc.add_paragraph(), after=4, line=0.8)

    # ---------------- cover: author comment (+ colour legend + study strategy)
    if box_cover:
        cb = doc.add_table(rows=1, cols=1)
        cb.alignment = WD_TABLE_ALIGNMENT.CENTER
        cc = cb.cell(0, 0); _box(cc, sz=6)
        p = cc.paragraphs[0]; _fmt(p, before=4, after=6)
        r = p.add_run("작성자 코멘트"); _font(r, F, 11, bold=True, underline=True)
        container = cc
    else:
        p = doc.add_paragraph(); _fmt(p, before=8, after=4)
        r = p.add_run("작성자 코멘트"); _font(r, F, 13, bold=True)
        container = doc
    if meta.get("comment"):
        for para in meta["comment"].split("\n"):
            p = container.add_paragraph(); _fmt(p, after=2 if dense else 3, line=1.2 if dense else 1.3, left=0.2)
            r = p.add_run(para); _font(r, F, 8.5 if dense else 9)
    _tips(container, note, F, 8.5 if dense else 9)
    _legend_lines(container, note, tpl, F, stacked=box_cover)
    if box_cover:
        _fmt(cc.add_paragraph(), after=2, line=0.6)

    # ---------------- TOC (차례)
    if box_cover:
        p = doc.add_paragraph(); _fmt(p, before=10, after=6)
        r = p.add_run("목차"); _font(r, F, 11, bold=True, underline=True)
    else:
        _banner(doc, "차 례", F, fill=TEAL_DARK, size=20, before=10, after=6)
    last_ch = None
    chapter_toc = tpl.format.toc_level == "chapter"
    for i, t in enumerate(note.topics):
        n = nums[i]
        if n["toc"] is None:
            continue
        if chapter_toc and n["chapter"]:  # one line per chapter, page of its first §
            if n["chapter"] == last_ch:
                continue
            last_ch = n["chapter"]
            p = doc.add_paragraph()
            _fmt(p, before=3, after=3, line=1.1, left=0.2)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(text_width), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            r = p.add_run(n["chapter"]); _font(r, F, 11, bold=True)
            r = p.add_run("\t"); _font(r, F, 11)
            _field(p, f"PAGEREF _Toc{i} \\h", str(page_map.get(i, "")), F, 11, bold=True)
            r = p.add_run("p"); _font(r, F, 11, bold=True)
            continue
        if n["chapter"] and n["chapter"] != last_ch:
            p = doc.add_paragraph(); _fmt(p, before=8, after=3, line=1.1, left=0.2)
            r = p.add_run(n["chapter"]); _font(r, F, 11.5, bold=True)
            last_ch = n["chapter"]
        elif not n["chapter"]:
            last_ch = None
        p = doc.add_paragraph()
        _fmt(p, after=4 if box_cover else 3, line=1.1, left=0.9 if n["chapter"] else (0.9 if box_cover else 0.2))
        p.paragraph_format.tab_stops.add_tab_stop(Cm(text_width), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        r = p.add_run(n["toc"]); _font(r, F, 10.5, bold=box_cover or None)
        r = p.add_run("\t"); _font(r, F, 10.5)
        _field(p, f"PAGEREF _Toc{i} \\h", str(page_map.get(i, "")), F, 10.5, bold=True)
        r = p.add_run("p"); _font(r, F, 10.5, bold=True)

    # ---------------- learning objectives (학습목표)
    objectives = [x for x in (meta.get("objectives") or "").split("\n") if x.strip()]
    if objectives:
        p = doc.add_paragraph(); _fmt(p, before=8 if dense else 16, after=3)
        r = p.add_run("학습목표"); _font(r, F, 12 if dense else 14, bold=True)
        for k, o in enumerate(objectives, start=1):
            p = doc.add_paragraph(); _fmt(p, after=1 if dense else 2, line=1.15 if dense else 1.25, left=0.2)
            for text, col, bold in runs(f"{k}. {o}"):
                r = p.add_run(text); _run_style(r, col, F, 9 if dense else 10, bold=True if bold else None)

    # ---------------- topics: one Word section (= new page + own header) per topic
    hs = tpl.format.heading_style
    mode = tpl.format.page_break  # "topic" | "chapter" | "flow"
    by_chapter = mode in ("chapter", "flow")
    for i, t in enumerate(note.topics):
        n = nums[i]
        prev = nums[i - 1] if i else None
        new_chapter = prev is not None and n["chapter"] != prev["chapter"]
        new_page = (not by_chapter or prev is None or n["front"] or prev["front"] or not n["chapter"]
                    or (mode == "chapter" and new_chapter))
        if not new_page:  # keep flowing on the current page
            if new_chapter:  # flow mode: the chapter banner goes into the body instead of a new page
                _banner(doc, n["banner"], F, fill=TEAL_DARK, size=15, before=14, after=4).paragraph_format.keep_with_next = True
            _section_heading(doc, n["section"], F, base, i)
        else:
            s_ = doc.add_section(WD_SECTION.NEW_PAGE)
            s_.left_margin = s_.right_margin = Cm(1.8)
            s_.top_margin, s_.bottom_margin = Cm(1.6), Cm(1.6)
            s_.header_distance = Cm(0.9)
        if not new_page:
            pass  # heading already written
        elif mode == "flow" and not n["front"] and n["chapter"]:  # one long section: banners live in the body
            _page_header(s_.header, None, None, None, F, tpl)
            _banner(doc, n["banner"], F, fill=TEAL_DARK, size=15, before=0, after=4).paragraph_format.keep_with_next = True
            _section_heading(doc, n["section"], F, base, i)
        elif by_chapter and not n["front"] and n["chapter"]:  # chapter banner in the header, § heading in the body
            _page_header(s_.header, None, n["banner"], None, F, tpl)
            _section_heading(doc, n["section"], F, base, i)
        elif hs == "banner":
            _page_header(s_.header, None, n["banner"], None if n["front"] else n["section"], F, tpl)
            p = doc.add_paragraph()
            _fmt(p, after=2, line=1.0)
            _bookmark(p, f"_Toc{i}", i + 1)
        else:  # plain / yellow-marker heading in the body, header = page number only
            _page_header(s_.header, None, None, None, F, tpl)
            if n["chapter"]:
                cp = doc.add_paragraph(); _fmt(cp, before=4, after=0, line=1.0)
                r = cp.add_run(n["chapter"]); _font(r, F, 9, color=COLOR["minor"])
            p = doc.add_paragraph()
            _fmt(p, before=6, after=10, line=1.15, left=0.0)
            r = p.add_run(n["section"]); _font(r, F, 17, bold=True)
            if hs == "marker":
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            _bookmark(p, f"_Toc{i}", i + 1)
        if t.basics and tpl.format.basics_box:
            _basics_box(doc, t, (n.get("no") or 1), F, base)
        if t.tip and tpl.format.topic_tips:
            _tip_line(doc, t, F, base)
        for sc in tpl.sections:
            sts = t.sections.get(sc.key)
            if not sts:
                continue
            if sc.label:
                hp2 = doc.add_paragraph(); _fmt(hp2, before=6, after=4)
                r = hp2.add_run(sc.label); _font(r, F, 11, bold=True)
            k = 0
            while k < len(sts):
                st = sts[k]
                if st.kind == "row2":  # consecutive rows form one table
                    j = k
                    while j < len(sts) and sts[j].kind == "row2":
                        j += 1
                    _row2_table(doc, sts[k:j], tpl)
                    k = j
                    continue
                if st.kind == "quiz":
                    _quiz_box(doc, st, tpl)
                else:
                    _statement(doc, st, note, tpl)
                k += 1
        for tb_ in t.tables:
            if tb_.rows:
                _table(doc, tb_, tpl)
        for img in t.images:
            if tpl.format.preserve_original_images and Path(img).exists():
                doc.add_picture(img, width=Cm(12))
        for f in t.review_flags:
            p = doc.add_paragraph(); _fmt(p, after=4, left=0.2)
            r = p.add_run(f"※ 검증 필요: {f}"); _font(r, F, 9, color=COLOR["verify"])

    if note.review_flags:
        p = doc.add_paragraph(); _fmt(p, before=14, after=4)
        r = p.add_run("검토 필요 항목"); _font(r, F, 11, bold=True)
        for f in note.review_flags:
            p = doc.add_paragraph(); _fmt(p, after=3, left=0.6)
            r = p.add_run(f"- {f}"); _font(r, F, 9, color=COLOR["verify"])

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out
