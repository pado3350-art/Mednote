"""Orchestrates stages and persists intermediate JSON so any stage can be re-run."""
from __future__ import annotations

import json
from pathlib import Path

from .align_content import align
from .export_docx import export_docx, export_markdown
from .extract_slides import extract_pptx
from .generate_notes import Backend, generate_note
from .models import Issue, AlignedSlide, ValidationReport
from .template import load_template
from .pdf_render import heading_pages, render_pdf
from .diagrams import render_diagram
from .exam import EXAM_BASE
from .generate_notes import OfflineBackend
from .figures import (apply_overrides, collect_figures, extract_pdf_slides, place_figures, save_figures,
                      slide_figures)
from .models import Outline, OutlineItem
from .outline import heuristic_outline, load_outline, normalize_outline, save_outline
from .material import extract_docx_material
from .models import AlignedSlide
from .transcript import is_structured, parse_flow_script, parse_script, read_script_text
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


def _auto_cover(note) -> None:
    """Offline mode: fill 학습목표 / 공부 전략 on the cover when the user gave none (rule-based, no AI)."""
    body = [t for t in note.topics if t.role == "body" and t.heading != "부록 & 검증 참고"]
    if body and not note.meta.get("objectives"):
        note.meta["objectives"] = "\n".join(f"'{t.heading}'을(를) 설명할 수 있다." for t in body[:6])
    if not note.meta.get("tips"):
        tips = []
        n_blue = sum(1 for t in note.topics for sts in t.sections.values() for s in sts
                     if "{b|" in s.text or "{c|" in s.text)
        if n_blue:
            tips.append("기출(PAD)에 나온 내용은 파랑으로 표시했습니다. 파랑 글씨부터 먼저 외우세요.")
        if any(t.tip for t in body):
            tips.append("교수님 강조 내용은 각 파트의 [공부 팁] 줄에 모아 두었습니다.")
        tips.append("시간이 없다면 [요약 정리]의 도식만 보고, 막히는 곳만 본문으로 돌아오세요.")
        note.meta["tips"] = "\n".join(tips)


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
    figures: list[str | Path] | None = None,  # extra picture sources: PDF / PPTX / image folder
    figures_json: str | Path | None = None,  # hand-edited placement log to re-apply
    max_figures_per_topic: int = 6,
    keep_text_images: bool = False,
    summary_figures: int = 4,
    name: str | None = None,
) -> tuple[ValidationReport, dict[str, Path]]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tpl = load_template(template_path)
    stem = name or Path(pptx or script).stem  # base name of the output files

    unit_labels: dict[int, str] = {}
    meta = dict(meta or {})
    notes_units: list[int] = []
    ref_style = "slide"
    if pptx:
        suffix = Path(pptx).suffix.lower()
        if suffix == ".pdf":  # slides given as PDF: one unit per page
            slides, _ = extract_pdf_slides(pptx, out / "images")
        elif suffix == ".docx":  # lecture material as a Word file (slide text + pictures)
            slides = extract_docx_material(pptx, out / "images")
        else:
            slides = extract_pptx(pptx, out / "images")
        aligned = []
        if script:
            text = read_script_text(script)
            if is_structured(text):  # block-headed script: read as one flow, drop the time blocks
                file_meta, segs = parse_flow_script(text)
                meta = {**{k: v for k, v in file_meta.items() if k in ("date", "subject")}, **meta}
                title = title or file_meta.get("title")
                speech = [g for g in segs if g.kind == "speech"]
                aligned = align(speech, slides, tpl.quality.min_alignment_confidence)
                notes_segs = [g for g in segs if g.kind == "note"]
                if notes_segs:  # remarks about the script itself: kept (appendix), cited by segment id only
                    aligned.append(AlignedSlide(slide_number=0, segments=notes_segs, method="none"))
            else:
                aligned = align(parse_script(text), slides, tpl.quality.min_alignment_confidence)
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
    note.pad_professors = {it.number: it.professor for it in exam_items}
    if getattr(backend, "authors_exam", False):  # hand-authored note: the author placed every paragraph, so the
        note.meta["alignment_reviewed"] = "1"  # automatic low-confidence alignment warnings do not apply
    if isinstance(backend, OfflineBackend) or backend is None:
        _auto_cover(note)
    if outline is None and ref_style == "para":
        outline = _outline_from_topics(note.topics)

    # ---- schematics: render every kind="diagram" statement to a picture
    n_dia = 0
    for t in note.topics:
        for sts in t.sections.values():
            for st in sts:
                if st.kind == "diagram" and st.diagram is not None:
                    n_dia += 1
                    st.image = str(render_diagram(st.diagram, out / "diagrams" / f"diagram_{n_dia:02d}.png"))

    # ---- pictures: slide images (bound to their slide) + extra sources (matched by text)
    all_figs = slide_figures(slides)
    if all_figs:
        for t in note.topics:
            t.images = []  # they are placed inline next to the related statements instead
    if figures:
        all_figs += collect_figures(figures, out / "figures")
    for i, f in enumerate(all_figs, start=1):
        f.id = i
    if all_figs:
        if figures_json:
            apply_overrides(all_figs, figures_json)
        place_figures(note, all_figs, tpl, max_per_topic=max_figures_per_topic, keep_text_images=keep_text_images,
                      summary_figures=summary_figures)
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

            pm = heading_pages(first, [n["section"] for n in numbering(note, tpl.format.roman_headings)])
            export_docx(note, tpl, docx_path, report, page_map=pm)
            pdf_path = render_pdf(docx_path, out)
    elif pdf:
        pdf_path = render_pdf(docx_path, out)

    # ---- page budget: a note should not be much longer than the lecture deserves (MOM handouts: ~6 min / page)
    if pdf_path and script and tpl.format.minutes_per_page > 0:
        from .pdf_render import page_texts
        from .transcript import lecture_minutes, page_budget

        sts = [st for t in note.topics for v in t.sections.values() for st in v]
        budget = page_budget(lecture_minutes(read_script_text(script)), tpl.format.minutes_per_page,
                             sum(st.kind == "check" for st in sts), sum(st.kind == "quiz" for st in sts))
        pages = page_texts(pdf_path)
        n_pages = len(pages) - (1 if pages and not pages[-1].strip() else 0)  # pdftotext ends with a form feed
        note.meta["page_budget"], note.meta["pages"] = str(budget), str(n_pages)
        if budget and n_pages > budget * 1.15:
            report.issues.append(Issue(severity="warning", code="PAGE_BUDGET", slide=None,
                                       message=f"{n_pages}쪽 — 강의 길이 기준 목표 {budget}쪽을 넘습니다. "
                                               "반복(기본정석·요약·본문)과 쪽 나눔을 줄이거나 mom_compact 템플릿을 쓰세요."))

    paths = {
        "slides": dump("slides.json", slides),
        "alignment": dump("alignment.json", aligned),
        "note": dump("note.json", note),
        **({"outline": save_outline(outline, out / "outline.json")} if outline else {}),
        **({"figures": save_figures(all_figs, out / "figures.json")} if all_figs else {}),
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
