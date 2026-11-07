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
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
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


def _fmt(p, before=0, after=6, line=1.3, left=None, first=None, align=None):
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
    if left is not None:
        pf.left_indent = Cm(left)
    if first is not None:
        pf.first_line_indent = Cm(first)
    if align is not None:
        p.alignment = align


def _box(cell, sz=12, color="000000"):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "single")
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


def numbering(note: LectureNote) -> list[dict]:
    """Per topic: chapter no/title and § no -> display strings (shared by TOC, banners, page lookup)."""
    out, ch_no, sec_no, last_ch = [], 0, 0, None
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
            out.append({"front": False, "chapter": "", "section": t.heading, "banner": t.heading,
                        "toc": t.heading, "no": 0})
    return out


def source_tag(st: Statement, note: LectureNote) -> str:
    return format_refs(st.slide_refs, note, st.time_ranges)


# --------------------------------------------------------------- statements
def _figure(doc, st: Statement, tpl: Template) -> None:
    """Centered picture (<= 14 x 9 cm, aspect kept) + small gray caption 'Figure n. ...'."""
    from PIL import Image

    F = tpl.format.font_korean
    path = Path(st.image)
    if not path.exists():
        return
    doc._fig_n = getattr(doc, "_fig_n", 0) + 1
    with Image.open(path) as im:
        w, h = im.size
    width_cm = min(14.0, 9.0 * w / max(h, 1))
    p = doc.add_paragraph()
    _fmt(p, before=6, after=2, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    c = doc.add_paragraph()
    _fmt(c, after=8, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = c.add_run(f"그림 {doc._fig_n}. {_strip(st.text)}")
    _font(r, F, 8.5, color=COLOR["minor"])


def _statement(doc, st: Statement, note: LectureNote, tpl: Template):
    if st.kind == "figure":
        _figure(doc, st, tpl)
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
        c = COLOR[col] if col else base_color
        _font(r, F, size, bold=True if (bold or base_bold) else None, color=c)
    if tpl.format.include_source_references and st.kind == "para":
        tag = source_tag(st, note)
        if tag:
            r = p.add_run(f"  [{tag}]")
            _font(r, F, 7, color=GRAY_TAG)


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
                _font(r, F, tpl.format.font_size_pt - 1, bold=True if (bold or ri == 0 or ci == 0) else None,
                      color=COLOR[col] if col else BLACK)
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
            _font(r, F, base + 0.5, bold=True if bold else None, color=COLOR[col] if col else BLACK)
    _fmt(c.add_paragraph(), after=0, line=0.6)
    _fmt(doc.add_paragraph(), after=4)


# ------------------------------------------------------------------- export
def export_mom(
    note: LectureNote, tpl: Template, out_path: str | Path, page_map: dict[int, int] | None = None
) -> Path:
    F = tpl.format.font_korean
    base = tpl.format.font_size_pt
    page_map = page_map or {}
    nums = numbering(note)
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

    # ---------------- cover: header box
    _page_header(sec.header, None, None, None, F, tpl)
    box = doc.add_table(rows=1, cols=1)
    box.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = box.cell(0, 0)
    _box(cell, sz=24)
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
    p = cell.add_paragraph(); _fmt(p, before=2, after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run(note.title); _font(r, F, 20, bold=True)
    p = cell.add_paragraph(); _fmt(p, after=6, align=WD_ALIGN_PARAGRAPH.RIGHT)
    r = p.add_run(meta.get("author", "")); _font(r, F, 9.5)

    # ---------------- cover: title banner + professor
    if meta.get("edition"):
        p = doc.add_paragraph(); _fmt(p, before=14, after=2, align=WD_ALIGN_PARAGRAPH.RIGHT)
        r = p.add_run(meta["edition"]); _font(r, F, 14, bold=True, color=RGBColor(0xFF, 0x4B, 0x2B))
    if meta.get("series"):
        _banner(doc, "", F, fill=SALMON, size=6, before=2, after=0).paragraph_format.left_indent = Cm(0)
        p = doc.add_paragraph(); _fmt(p, before=8, after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(meta["series"]); _font(r, F, 40, bold=True)
    tb = _banner(doc, note.title, F, fill=SALMON, size=24, before=10, after=0)
    tb.paragraph_format.left_indent = Cm(0); tb.paragraph_format.right_indent = Cm(0)
    tb.paragraph_format.space_before = Pt(10)
    if meta.get("professor"):
        p = doc.add_paragraph(); _fmt(p, before=10, after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(meta["professor"]); _font(r, F, 24, bold=True)
        r = p.add_run(" 교수님"); _font(r, F, 14, bold=True)

    # ---------------- cover: comment + legend
    used = {s.tag for t in note.topics for sts in t.sections.values() for s in sts}
    for t in note.topics:
        for sts in t.sections.values():
            for s in sts:
                if s.emphasis:
                    used.add("emphasis")
                for m in re.finditer(r"\{([rbgp])\|", s.text):
                    used.add({"r": "emphasis", "b": "exam", "g": "minor", "p": "verify"}[m.group(1)])
        for line in t.basics:
            for m in re.finditer(r"\{([rbgp])\|", line):
                used.add({"r": "emphasis", "b": "exam", "g": "minor", "p": "verify"}[m.group(1)])
    p = doc.add_paragraph(); _fmt(p, before=8, after=4)
    r = p.add_run("작성자 코멘트"); _font(r, F, 13, bold=True)
    if meta.get("comment"):
        for para in meta["comment"].split("\n"):
            p = doc.add_paragraph(); _fmt(p, after=3, line=1.3, left=0.2)
            r = p.add_run(para); _font(r, F, 9)
    legend = [i for i in tpl.format.legend if i.tag in used]
    if legend:
        p = doc.add_paragraph(); _fmt(p, before=2, after=4, left=0.2)
        for k, item in enumerate(legend):
            r = p.add_run(("    " if k else "") + item.word); _font(r, F, 8.5, bold=True, color=COLOR[item.tag])
            r = p.add_run(f" : {item.meaning}"); _font(r, F, 8.5)

    # ---------------- TOC (차례)
    _banner(doc, "차 례", F, fill=TEAL_DARK, size=20, before=10, after=6)
    last_ch = None
    for i, t in enumerate(note.topics):
        n = nums[i]
        if n["toc"] is None:
            continue
        if n["chapter"] and n["chapter"] != last_ch:
            p = doc.add_paragraph(); _fmt(p, before=8, after=3, line=1.1, left=0.2)
            r = p.add_run(n["chapter"]); _font(r, F, 11.5, bold=True)
            last_ch = n["chapter"]
        elif not n["chapter"]:
            last_ch = None
        p = doc.add_paragraph()
        _fmt(p, after=3, line=1.1, left=0.9 if n["chapter"] else 0.2)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(text_width), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        r = p.add_run(n["toc"]); _font(r, F, 10.5)
        r = p.add_run("\t"); _font(r, F, 10.5)
        _field(p, f"PAGEREF _Toc{i} \\h", str(page_map.get(i, "")), F, 10.5, bold=True)
        r = p.add_run("p"); _font(r, F, 10.5, bold=True)

    # ---------------- topics: one Word section (= new page + own header) per topic
    sec_no_in_chapter = 0
    for i, t in enumerate(note.topics):
        n = nums[i]
        s_ = doc.add_section(WD_SECTION.NEW_PAGE)
        s_.left_margin = s_.right_margin = Cm(1.8)
        s_.top_margin, s_.bottom_margin = Cm(1.6), Cm(1.6)
        s_.header_distance = Cm(0.9)
        _page_header(s_.header, None, n["banner"], None if n["front"] else n["section"], F, tpl)
        p = doc.add_paragraph()
        _fmt(p, after=2, line=1.0)
        _bookmark(p, f"_Toc{i}", i + 1)
        if t.basics:
            _basics_box(doc, t, (n.get("no") or 1), F, base)
        for s in tpl.sections:
            sts = t.sections.get(s.key)
            if not sts:
                continue
            if s.label:
                hp2 = doc.add_paragraph(); _fmt(hp2, before=6, after=4)
                r = hp2.add_run(s.label); _font(r, F, 11, bold=True)
            for st in sts:
                _statement(doc, st, note, tpl)
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
