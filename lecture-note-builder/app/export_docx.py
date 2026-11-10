"""Stage 5: LectureNote -> DOCX / Markdown. Code (not the AI) owns all styling."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

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
    labels = {"exam": "**[기출]** ", "exam_other": "**[다른 교수님 기출]** "}
    parts = []
    last_color = None
    for value, color, bold in _runs(text):
        if color != last_color:
            parts.append(labels.get(color, ""))
        parts.append(f"**{value}**" if bold else value)
        last_color = color
    return "".join(parts)


def source_tag(st: Statement, note: LectureNote) -> str:
    return format_refs(st.slide_refs, note, st.time_ranges, st.segment_ids)


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
    if st.kind in ("figure", "diagram"):
        from .export_mom import _figure

        _figure(doc, st, tpl)
        return
    if st.kind in ("rows", "qa"):
        from .export_mom import _qa_box, _rows_table

        {"rows": _rows_table, "qa": _qa_box}[st.kind](doc, st, tpl)
        return
    if st.kind in ("figure_side", "columns", "concept", "check"):
        from .export_mom import _check_box, _columns_box, _concept_box, _figure_side

        if st.kind == "check":
            _check_box(doc, [st], tpl, answers_inline=True)
        else:
            {"figure_side": _figure_side, "columns": _columns_box, "concept": _concept_box}[st.kind](doc, st, tpl)
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


def _md_table(rows: list[list[str]]) -> list[str]:
    if not rows or not (width := max(map(len, rows))):
        return []
    lines = []
    for row in rows:
        cells = [_md(cell).replace("|", r"\|").replace("\n", "<br>") for cell in row]
        lines.append("| " + " | ".join(cells + [""] * (width - len(cells))) + " |")
    return ["", lines[0], "|" + "---|" * width, *lines[1:], ""]


def _md_image(image: str, caption: str, folder: Path) -> str:
    path = Path(image)
    caption = _strip(caption) or path.name
    if not image or not path.is_file():
        return f"*그림: {caption} (파일 없음)*"
    try:
        relative = Path(os.path.relpath(path.resolve(), folder.resolve())).as_posix()
    except ValueError:
        return f"*그림: {caption} (문서와 다른 드라이브에 있음)*"
    alt = caption.replace("[", r"\[").replace("]", r"\]").replace("\n", " ")
    return f"![{alt}]({quote(relative, safe='/')})"


def export_markdown(note: LectureNote, tpl: Template, out_path: str | Path) -> Path:
    out = Path(out_path)
    L = [f"# {note.title}", ""]
    if tpl.format.layout == "mom":
        for key, label in (("comment", "작성자 코멘트"), ("tips", "먼저 볼 내용"), ("objectives", "학습목표")):
            lines = note.meta.get(key, "").splitlines()
            if lines:
                L += [f"**{label}**", "", *[f"- {_md(line)}" for line in lines if line.strip()], ""]

    contents = []
    body_lines = []
    chapter = ""
    chapter_number = 0
    section_number = 0
    for i, t in enumerate(note.topics, start=1):
        grouped = t.role == "body" and bool(t.chapter)
        if grouped and t.chapter != chapter:
            chapter_number += 1
            section_number = 0
            chapter_title = f"{chapter_number}장. {t.chapter}" if tpl.format.numbered_headings else t.chapter
            anchor = f"chapter-{chapter_number}"
            contents.append(f"- [{chapter_title}](#{anchor})")
            body_lines += [f'<a name="{anchor}"></a>', "", f"## {chapter_title}", ""]
        chapter = t.chapter if grouped else ""
        section_number += 1
        anchor = f"topic-{i}"
        prefix = f"{section_number if grouped else i}. " if tpl.format.numbered_headings else ""
        heading = prefix + t.heading
        if not grouped:
            contents.append(f"- [{heading}](#{anchor})")
        body_lines += [f'<a name="{anchor}"></a>', "", f"{'###' if grouped else '##'} {heading}", ""]
        if tpl.format.include_source_references:
            refs = format_refs(t.slide_numbers, note)
            if refs:
                body_lines += [f"*{refs}*", ""]
        if tpl.format.basics_box and t.basics:
            body_lines += [f"**{t.basics_title or tpl.format.basics_label}**", ""]
            body_lines += [f"- {_md(item)}" for item in t.basics]
            if tpl.format.include_source_references and (refs := format_refs(t.basics_refs, note)):
                body_lines += ["", f"*{refs}*"]
            body_lines.append("")
        if tpl.format.topic_tips and t.tip:
            body_lines += [f"> **공부 팁** {_md(t.tip)}", ""]
        for sec in tpl.sections:
            sts = t.sections.get(sec.key)
            if not sts:
                continue
            if sec.label.strip():
                body_lines += [f"{'####' if grouped else '###'} {sec.label}", ""]
            for st in sts:
                if st.kind in ("figure", "diagram"):
                    body_lines += ["", _md_image(st.image, st.text, out.parent), ""]
                    continue
                if st.kind == "figure_side":
                    if st.image:
                        body_lines += ["", _md_image(st.image, st.text, out.parent), ""]
                    if st.left_title:
                        body_lines.append(f"**{_md(st.left_title)}**")
                    body_lines += [f"- {_md(x.removeprefix('- '))}" for x in st.left]
                    continue
                if st.kind == "quiz":
                    body_lines += ["", f"**문제** {_md(st.text)}", "", *[f"- {_md(x)}" for x in st.options], ""]
                    if st.answer or st.explanations:
                        body_lines += ["<details>", "<summary>정답과 해설</summary>", ""]
                        if st.answer:
                            body_lines += [f"**정답:** {_md(st.answer)}", ""]
                        body_lines += [*[f"- {_md(x)}" for x in st.explanations], "", "</details>", ""]
                    continue
                if st.kind == "rows":
                    n_c = max((len(r) for r in st.rows), default=0)
                    if st.col_titles:
                        L.append("| " + " | ".join(_md(x) for x in st.col_titles) + " |")
                        L.append("|" + "---|" * len(st.col_titles))
                    elif n_c:
                        L.append("| " + " | ".join([" "] * n_c) + " |")
                        L.append("|" + "---|" * n_c)
                    for r in st.rows:
                        L.append("| " + " | ".join(_md(x).replace("\n", "<br>") for x in r) + " |")
                    continue
                if st.kind == "qa":
                    L.append(f"> **{_md(st.left_title)}** {_md(st.text)}")
                    L += [f"- A. {_md(x)}" if k == 0 else f"  {_md(x)}" for k, x in enumerate(st.left)]
                    continue
                if st.kind == "check":
                    body_lines.append(f"- **개념 Check** {_md(st.text)} (O, X) → {st.answer}" + (f" — {_md(st.explanations[0])}" if st.explanations else ""))
                    continue
                if st.kind == "concept":
                    body_lines.append(f"> **개념 정리** {_md(st.left_title)}")
                    body_lines += [f"> - {_md(x.removeprefix('- '))}" for x in st.left]
                    if st.image:
                        body_lines += ["", _md_image(st.image, st.text, out.parent), ""]
                    continue
                if st.kind == "columns" and st.diagram is not None:
                    gs = st.diagram.groups
                    body_lines += _md_table([[g.title for g in gs], ["<br>".join(g.items) for g in gs]])
                    continue
                pre = "▶ **교수님:** " if st.origin == "lecturer" else ""
                body = f"**{_md(st.text)}**" if st.emphasis else _md(st.text)
                if st.origin == "author" and not body.lstrip().startswith("("):
                    body = f"({body})"
                if st.effort:
                    body += f" [{st.effort}]"
                tag = source_tag(st, note)
                line = f"{pre}{body}" + (f" `[{tag}]`" if tag and tpl.format.include_source_references else "")
                if t.style == "explain" and st.kind == "para":
                    body_lines += ["", line, ""]
                else:
                    body_lines.append(f"- {line}")
            body_lines.append("")
        for tb in t.tables:
            body_lines += _md_table(tb.rows)
        for img in t.images:
            body_lines += ["", _md_image(img, "", out.parent), ""]
        body_lines.append("")
    if contents:
        L += ["## 목차", "", *contents, ""]
    L += body_lines
    if note.exam_points:
        L += ["## 시험 포인트", *[f"- {_md(s.text)} `[{source_tag(s, note)}]`" for s in note.exam_points], ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    return out
