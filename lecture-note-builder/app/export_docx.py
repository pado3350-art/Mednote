"""Stage 5: LectureNote -> DOCX / Markdown. Code (not the AI) owns all styling."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from .refs import format_refs
from .markup import runs as _runs, strip as _strip
from .models import LectureNote, Statement, ValidationReport
from .template import Template

GRAY = RGBColor(0x6B, 0x72, 0x80)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)
RED = RGBColor(0xB9, 0x1C, 0x1C)


def _md(text: str) -> str:
    return "".join(f"**{t}**" if b else t for t, _, b in _runs(text))


def source_tag(st: Statement, note: LectureNote) -> str:
    return format_refs(st.slide_refs, note, st.time_ranges)


def _set_font(run, name: str, size: float | None = None) -> None:
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if size:
        run.font.size = Pt(size)


def _style_doc(doc: Document, tpl: Template) -> None:
    for style_name in ("Normal", "Heading 1", "Heading 2", "Heading 3", "Title", "List Bullet"):
        st = doc.styles[style_name]
        st.font.name = tpl.format.font_korean
        st.element.rPr.rFonts.set(qn("w:eastAsia"), tpl.format.font_korean)
    doc.styles["Normal"].font.size = Pt(tpl.format.font_size_pt)
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)


def _statement(doc: Document, st: Statement, tpl: Template, lecturer: bool, note: LectureNote) -> None:
    if st.kind == "figure":
        from .export_mom import _figure

        _figure(doc, st, tpl)
        return
    p = doc.add_paragraph(style="List Bullet")
    if lecturer:
        r0 = p.add_run("▶ 교수님: ")
        r0.bold = True
        r0.font.color.rgb = BLUE
    r = p.add_run(_strip(st.text.strip()))
    if st.emphasis:
        r.bold = True
    if lecturer:
        r.italic = True
    if tpl.format.include_source_references:
        tag = source_tag(st, note)
        if tag:
            rt = p.add_run(f"  [{tag}]")
            rt.font.size = Pt(8)
            rt.font.color.rgb = GRAY


def export_docx(
    note: LectureNote,
    tpl: Template,
    out_path: str | Path,
    report: ValidationReport | None = None,
    page_map: dict[int, int] | None = None,
) -> Path:
    if tpl.format.layout == "mom":
        from .export_mom import export_mom

        return export_mom(note, tpl, out_path, page_map)
    doc = Document()
    _style_doc(doc, tpl)
    doc.add_heading(note.title, level=0)

    for i, t in enumerate(note.topics, start=1):
        prefix = f"{i}. " if tpl.format.numbered_headings else ""
        doc.add_heading(prefix + t.heading, level=1)
        refs = "PPT p." + ",".join(map(str, t.slide_numbers))
        meta = doc.add_paragraph()
        mr = meta.add_run(refs)
        mr.font.size = Pt(8)
        mr.font.color.rgb = GRAY

        for sec in tpl.sections:
            sts = t.sections.get(sec.key)
            if not sts:
                continue
            doc.add_heading(sec.label, level=3)
            for st in sts:
                _statement(doc, st, tpl, lecturer=st.origin == "lecturer", note=note)

        for tb in t.tables:
            if not tb.rows:
                continue
            table = doc.add_table(rows=len(tb.rows), cols=max(len(r) for r in tb.rows))
            table.style = "Table Grid"
            for ri, row in enumerate(tb.rows):
                for ci, cell in enumerate(row):
                    c = table.cell(ri, ci)
                    c.text = cell
                    if ri == 0:
                        for run in c.paragraphs[0].runs:
                            run.bold = True
            doc.add_paragraph()

        if tpl.format.preserve_original_images:
            for img in t.images:
                if Path(img).exists():
                    doc.add_picture(img, width=Cm(11))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

        for f in t.review_flags:
            p = doc.add_paragraph()
            r = p.add_run(f"⚠ 검토 필요: {f}")
            r.font.color.rgb = RED
            r.font.size = Pt(9)

    if note.exam_points:
        doc.add_heading("시험 포인트 (교수님 강조 모음)", level=1)
        for st in note.exam_points:
            _statement(doc, st, tpl, lecturer=True, note=note)

    if note.review_flags or (report and report.issues):
        doc.add_page_break()
        doc.add_heading("검토 필요 항목", level=1)
        for f in note.review_flags:
            doc.add_paragraph(f, style="List Bullet")
        if report:
            for iss in report.issues:
                if iss.severity != "info":
                    where = f"[{report.unit_names.get(iss.slide, f'슬라이드 {iss.slide}')}] " if iss.slide else ""
                    doc.add_paragraph(f"{iss.code} {where}{iss.message}", style="List Bullet")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def export_markdown(note: LectureNote, tpl: Template, out_path: str | Path) -> Path:
    L = [f"# {note.title}", ""]
    for i, t in enumerate(note.topics, start=1):
        prefix = f"{i}. " if tpl.format.numbered_headings else ""
        L += [f"## {prefix}{t.heading}", f"*PPT p.{','.join(map(str, t.slide_numbers))}*", ""]
        for sec in tpl.sections:
            sts = t.sections.get(sec.key)
            if not sts:
                continue
            L.append(f"### {sec.label}")
            for st in sts:
                if st.kind == "figure":
                    L.append(f"![{_md(st.text)}]({st.image})")
                    continue
                pre = "▶ **교수님:** " if st.origin == "lecturer" else ""
                body = f"**{_md(st.text)}**" if st.emphasis else _md(st.text)
                tag = source_tag(st, note)
                L.append(f"- {pre}{body}" + (f" `[{tag}]`" if tag and tpl.format.include_source_references else ""))
            L.append("")
        for tb in t.tables:
            if tb.rows:
                w = max(len(r) for r in tb.rows)
                rows = [r + [""] * (w - len(r)) for r in tb.rows]
                L.append("| " + " | ".join(rows[0]) + " |")
                L.append("|" + "---|" * w)
                L += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                L.append("")
        for img in t.images:
            L.append(f"![{Path(img).name}]({img})")
        L.append("")
    if note.exam_points:
        L += ["## 시험 포인트", *[f"- {s.text} `[{source_tag(s, note)}]`" for s in note.exam_points], ""]
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    return out
