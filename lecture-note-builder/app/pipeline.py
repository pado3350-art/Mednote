"""Orchestrates stages and persists intermediate JSON so any stage can be re-run."""
from __future__ import annotations

import json
from pathlib import Path

from .align_content import align
from .export_docx import export_docx, export_markdown
from .extract_slides import extract_pptx
from .generate_notes import Backend, generate_note
from .models import AlignedSlide, ValidationReport
from .template import load_template
from .pdf_render import heading_pages, render_pdf
from .transcript import is_structured, parse_script, parse_structured_script, read_script_text
from .validate_notes import report_markdown, validate


def _slides_from_units(units):
    from .models import BodyLine, Slide

    slides = [
        Slide(number=u.number, title=u.title, body=[BodyLine(text=t) for t in u.paragraphs])
        for u in units
    ]
    return slides, {u.number: u.label for u in units}


def run_pipeline(
    pptx: str | Path | None,
    out_dir: str | Path,
    template_path: str | Path,
    script: str | Path | None = None,
    backend: Backend | None = None,
    title: str | None = None,
    meta: dict[str, str] | None = None,
    pdf: bool = True,
) -> tuple[ValidationReport, dict[str, Path]]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tpl = load_template(template_path)
    stem = Path(pptx or script).stem

    unit_labels: dict[int, str] = {}
    meta = dict(meta or {})
    if pptx:
        slides = extract_pptx(pptx, out / "images")
        segments = parse_script(read_script_text(script)) if script else []
        aligned = align(segments, slides, tpl.quality.min_alignment_confidence)
    else:
        if not script:
            raise ValueError("PPTX 또는 스크립트 중 하나는 필요합니다.")
        text = read_script_text(script)
        if not is_structured(text):
            raise ValueError(
                "PPTX 없이 스크립트만 쓰려면 '[00:00–02:00] 제목 | 원본 2쪽' 형식의 구간 헤더가 필요합니다."
            )
        file_meta, units = parse_structured_script(text)
        slides, unit_labels = _slides_from_units(units)
        aligned = []
        meta = {**{k: v for k, v in file_meta.items() if k in ("date", "subject")}, **meta}
        title = title or file_meta.get("title")
    title = title or stem

    note = generate_note(title, slides, aligned, tpl, backend, meta=meta, unit_labels=unit_labels)
    report = validate(note, slides, aligned, tpl)

    def dump(name: str, objs) -> Path:
        p = out / name
        data = [o.model_dump() for o in objs] if isinstance(objs, list) else objs.model_dump()
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    docx_path = out / f"{stem}_강의록.docx"
    export_docx(note, tpl, docx_path, report)
    pdf_path = None
    if pdf and tpl.format.layout == "mom":
        # two passes: render, read where each heading landed, refill the TOC numbers
        first = render_pdf(docx_path, out)
        if first:
            from .export_mom import heading_text

            pm = heading_pages(first, [heading_text(i, t, tpl) for i, t in enumerate(note.topics)])
            export_docx(note, tpl, docx_path, report, page_map=pm)
            pdf_path = render_pdf(docx_path, out)
    elif pdf:
        pdf_path = render_pdf(docx_path, out)

    paths = {
        "slides": dump("slides.json", slides),
        "alignment": dump("alignment.json", aligned),
        "note": dump("note.json", note),
        "report_json": dump("validation.json", report),
        "docx": docx_path,
        "markdown": export_markdown(note, tpl, out / f"{stem}_강의록.md"),
    }
    if pdf_path:
        paths["pdf"] = pdf_path
    rp = out / "validation_report.md"
    rp.write_text(report_markdown(report), encoding="utf-8")
    paths["report"] = rp
    return report, paths
