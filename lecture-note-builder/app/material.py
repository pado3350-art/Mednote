"""Lecture material given as a DOCX (slides pasted/converted to Word): text + pictures -> slide units.

Unit = one slide. A new unit starts at a slide-title paragraph:
  * numbered titles  "6-10 Many proteins ..."          * "Chapter 6", "Chapter 6 part II. Summary 1"
  * "Introduction ...", "Generation of ...", "수업학습성과", "핵심 어휘"
Broken lines of one bullet are re-joined, embedded bullets are split, copyright footers are dropped.
Pictures keep their slide (document order) and get the slide's "Fig. x.y ..." line as caption.
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

from .models import BodyLine, Slide

TITLE_RES = [
    re.compile(r"^\d+\s*[-–]\s*\d+\s+\S"),
    re.compile(r"^Chapter\s+\d+\s*$", re.I),
    re.compile(r"^Chapter\s+\d+\s+part\s+\w+\.?\s*Summary", re.I),
    re.compile(r"^(수업\s*학습\s*성과|핵심\s*어휘|학습\s*목표)\s*$"),
    re.compile(r"^Introduction\b", re.I),
    re.compile(r"^Generation of\b", re.I),
]
BULLET = re.compile(r"^\s*([•▪◼◦⚫●○■□\-–*]|\d+[.)]|[①-⑳]|Fig\.)\s*")
FOOTER = re.compile(r"^(본\s*강의자료는|하는\s*모든\s*법적\s*책임)")
EMBEDDED = re.compile(r"\s+[•▪●]\s+")


def _is_title(t: str) -> bool:
    return any(r.match(t) for r in TITLE_RES)


def _iter_blocks(doc):
    """Yield ('p', text, [image blobs]) in document order."""
    rels = doc.part.rels
    for p in doc.paragraphs:
        blobs = []
        for blip in p._p.findall(".//" + qn("a:blip")):
            rid = blip.get(qn("r:embed"))
            if rid and rid in rels and "image" in rels[rid].reltype:
                blobs.append((rels[rid].target_part.blob, Path(rels[rid].target_part.partname).suffix or ".png"))
        yield " ".join(p.text.split()), blobs


def extract_docx_material(path: str | Path, image_dir: str | Path) -> list[Slide]:
    path, image_dir = Path(path), Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    doc = Document(str(path))
    units: list[dict] = []
    cur: dict | None = None

    def new_unit(title: str):
        nonlocal cur
        cur = {"title": title, "lines": [], "imgs": [], "caps": []}
        units.append(cur)

    for text, blobs in _iter_blocks(doc):
        if FOOTER.match(text):
            continue
        if text and _is_title(text):
            title, rest = text, ""
            m = re.search(r"\s[•▪●]\s|\s(?=Fig\.\s*\d)", text)  # title paragraph that also carries content
            if m and not re.match(r"^Chapter\s+\d+\s*$", text):
                title, rest = text[: m.start()].strip(), text[m.start():].strip(" •▪●")
            new_unit(title)
            if rest:
                cur["lines"].append(rest)
        elif cur is None and (text or blobs):
            new_unit(text or "표지")
            text = "" if text else text
        if cur is None:
            continue
        for k, (blob, ext) in enumerate(blobs):
            n = len(units)
            f = image_dir / f"material_s{n:02d}_{len(cur['imgs']) + 1}{ext}"
            f.write_bytes(blob)
            cur["imgs"].append(str(f))
        if text and not (_is_title(text) and cur["lines"] and cur["lines"][-1] == text):
            if cur["title"] != text and not (cur["lines"] == [] and text == cur["title"]):
                body = text
                if _is_title(text):
                    continue
                if BULLET.match(body) or not cur["lines"] or cur["lines"][-1].endswith((".", ":")) and False:
                    cur["lines"].append(body)
                else:
                    cur["lines"][-1] += " " + body  # broken line of the previous bullet
    slides: list[Slide] = []
    seen: dict[str, int] = {}
    for i, u in enumerate(units, start=1):
        lines: list[str] = []
        caps: list[str] = []
        for ln in u["lines"]:
            for part in [x for x in EMBEDDED.split(ln) if x.strip()]:
                part = part.strip()
                part = BULLET.sub("", part, count=1).strip() if not part.startswith("Fig.") else part
                if not part:
                    continue
                (caps if part.startswith("Fig.") else lines).append(part)
        title = u["title"]
        if title in seen:
            seen[title] += 1
            title = f"{title} ({seen[title]})"
        else:
            seen[title] = 1
        slides.append(Slide(number=i, title=title, body=[BodyLine(text=t) for t in lines],
                            images=u["imgs"], fig_captions=caps))
    # cover: "Chapter 6" + next short line "Antigen Presentation ..." -> one title
    if len(slides) >= 2 and slides[0].title.lower().startswith("chapter") and slides[0].body:
        first = slides[0]
        if len(first.body) >= 1 and len(first.body[0].text) <= 60:
            first.title = f"{first.title} · {first.body[0].text}"
            first.body = first.body[1:]
    return slides
