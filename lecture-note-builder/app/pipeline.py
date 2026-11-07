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
from .transcript import parse_script, read_script_text
from .validate_notes import report_markdown, validate


def run_pipeline(
    pptx: str | Path,
    out_dir: str | Path,
    template_path: str | Path,
    script: str | Path | None = None,
    backend: Backend | None = None,
    title: str | None = None,
) -> tuple[ValidationReport, dict[str, Path]]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tpl = load_template(template_path)
    stem = Path(pptx).stem
    title = title or stem

    slides = extract_pptx(pptx, out / "images")
    segments = parse_script(read_script_text(script)) if script else []
    aligned = align(segments, slides, tpl.quality.min_alignment_confidence)
    note = generate_note(title, slides, aligned, tpl, backend)
    report = validate(note, slides, aligned, tpl)

    def dump(name: str, objs) -> Path:
        p = out / name
        data = [o.model_dump() for o in objs] if isinstance(objs, list) else objs.model_dump()
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    paths = {
        "slides": dump("slides.json", slides),
        "alignment": dump("alignment.json", aligned),
        "note": dump("note.json", note),
        "report_json": dump("validation.json", report),
        "docx": export_docx(note, tpl, out / f"{stem}_강의록.docx", report),
        "markdown": export_markdown(note, tpl, out / f"{stem}_강의록.md"),
    }
    rp = out / "validation_report.md"
    rp.write_text(report_markdown(report), encoding="utf-8")
    paths["report"] = rp
    return report, paths
