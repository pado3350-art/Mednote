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
from .exam import EXAM_BASE
from .models import Outline, OutlineItem
from .outline import heuristic_outline, load_outline, normalize_outline, save_outline
from .transcript import parse_flow_script, parse_script, read_script_text
from .validate_notes import report_markdown, validate


def _units_from_segments(segments):
    """Script paragraphs become units (numbered 1..n) so the rest of the pipeline is unchanged."""
    from .models import BodyLine, Slide

    return [Slide(number=g.id, title="", body=[BodyLine(text=g.text)]) for g in segments]


def _outline_from_topics(topics) -> Outline:
    from .exam import EXAM_BASE

    return Outline(items=[OutlineItem(heading=t.heading, chapter=t.chapter,
                                      unit_numbers=[n for n in t.slide_numbers if n < EXAM_BASE])
                          for t in topics if t.role == "body" and any(n < EXAM_BASE for n in t.slide_numbers)])


def run_pipeline(
    pptx: str | Path | None,
    out_dir: str | Path,
    template_path: str | Path,
    script: str | Path | None = None,
    backend: Backend | None = None,
    title: str | None = None,
    meta: dict[str, str] | None = None,
    pdf: bool = True,
    exam_pdf: str | Path | None = None,
    toc: str | None = None,  # "ai" | "heuristic" | "unit" | None(auto)
    outline_json: str | Path | None = None,
) -> tuple[ValidationReport, dict[str, Path]]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tpl = load_template(template_path)
    stem = Path(pptx or script).stem

    unit_labels: dict[int, str] = {}
    meta = dict(meta or {})
    notes_units: list[int] = []
    ref_style = "slide"
    if pptx:
        slides = extract_pptx(pptx, out / "images")
        segments = parse_script(read_script_text(script)) if script else []
        aligned = align(segments, slides, tpl.quality.min_alignment_confidence)
        toc = toc or "unit"
    else:
        if not script:
            raise ValueError("PPTX 또는 스크립트 중 하나는 필요합니다.")
        file_meta, segments = parse_flow_script(read_script_text(script))
        if len(segments) >= EXAM_BASE:
            raise ValueError(f"스크립트 단락이 너무 많습니다({len(segments)}). {EXAM_BASE - 1}개 이하로 나누세요.")
        slides = _units_from_segments(segments)
        notes_units = [g.id for g in segments if g.kind == "note"]
        aligned = []
        ref_style = "para"
        meta = {**{k: v for k, v in file_meta.items() if k in ("date", "subject")}, **meta}
        title = title or file_meta.get("title")
        toc = toc or "ai"
    title = title or stem

    exam_items = []
    if exam_pdf:  # PAD (기출문제) units: citable sources, blue-text justification
        from .exam import parse_exam_pdf
        from .models import BodyLine, Slide

        exam_items = parse_exam_pdf(exam_pdf)
        for it in exam_items:
            body = [BodyLine(text=it.question), BodyLine(text=f"정답: {it.answer}")]
            if it.commentary:
                body.append(BodyLine(text=it.commentary))
            slides.append(Slide(number=it.number, title=it.title, body=body))
            unit_labels[it.number] = it.label

    # ---- table of contents (AI judges the overall flow)
    outline = None
    content_units = [s for s in slides if s.number < EXAM_BASE]
    speech = [s.number for s in content_units if s.number not in notes_units]
    if outline_json:
        outline = normalize_outline(load_outline(outline_json), speech, notes_units)
    elif getattr(backend, "authors_exam", False):
        outline = None  # authored topics define the TOC; outline.json is derived below
    elif toc in ("ai", "heuristic"):
        speech_units = [s for s in content_units if s.number in set(speech)]
        if toc == "ai" and hasattr(backend, "make_outline"):
            raw = backend.make_outline(speech_units, exam_items)
        else:
            if toc == "ai":
                print("※ AI 백엔드가 없어 휴리스틱 목차를 사용합니다 (--backend anthropic 또는 --outline-json 권장).")
            raw = heuristic_outline(speech_units)
        outline = normalize_outline(raw, speech, notes_units)

    note = generate_note(title, slides, aligned, tpl, backend, meta=meta, unit_labels=unit_labels,
                         outline=outline, exam_items=exam_items, ref_style=ref_style)
    if outline is None and ref_style == "para":
        outline = _outline_from_topics(note.topics)
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
            from .export_mom import numbering

            pm = heading_pages(first, [n["section"] for n in numbering(note)])
            export_docx(note, tpl, docx_path, report, page_map=pm)
            pdf_path = render_pdf(docx_path, out)
    elif pdf:
        pdf_path = render_pdf(docx_path, out)

    paths = {
        "slides": dump("slides.json", slides),
        "alignment": dump("alignment.json", aligned),
        "note": dump("note.json", note),
        **({"outline": save_outline(outline, out / "outline.json")} if outline else {}),
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
