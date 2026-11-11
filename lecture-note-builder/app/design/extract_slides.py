"""Stage 1a: PPTX -> list[Slide] (text, tables, images, speaker notes)."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from ..models import BodyLine, Slide, SlideTable


def _walk(shapes):
    """Yield leaf shapes, descending into groups, in top-then-left order."""
    ordered = sorted(shapes, key=lambda s: (s.top or 0, s.left or 0))
    for sh in ordered:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _walk(sh.shapes)
        else:
            yield sh


def extract_pptx(path: str | Path, image_dir: str | Path) -> list[Slide]:
    path, image_dir = Path(path), Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    prs = Presentation(str(path))
    slides: list[Slide] = []

    for idx, s in enumerate(prs.slides, start=1):
        title_shape = s.shapes.title
        title = title_shape.text_frame.text.strip() if title_shape is not None else ""
        slide = Slide(number=idx, title=title)

        for sh in _walk(s.shapes):
            if title_shape is not None and sh.shape_id == title_shape.shape_id:
                continue
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    text = "".join(r.text for r in p.runs).strip()
                    if text:
                        slide.body.append(BodyLine(text=text, level=p.level))
            elif getattr(sh, "has_table", False) and sh.has_table:
                rows = [[c.text.strip() for c in r.cells] for r in sh.table.rows]
                slide.tables.append(SlideTable(rows=rows))
            elif sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                img = sh.image
                out = image_dir / f"slide{idx:03d}_{len(slide.images) + 1}.{img.ext}"
                out.write_bytes(img.blob)
                slide.images.append(str(out))

        if s.has_notes_slide:
            slide.speaker_notes = s.notes_slide.notes_text_frame.text.strip()
        slides.append(slide)
    return slides
