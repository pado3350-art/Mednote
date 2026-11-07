"""Figures: pull pictures out of lecture material and place them next to the text they explain.

Sources (any number, any mix):  PDF (handouts, slide PDFs, finished notes)  /  PPTX  /  folder of images.
Pipeline:  extract (+ caption, + page-text context)  ->  match to a section by lexical similarity
(soft left-to-right order prior)  ->  anchor after the most related statement  ->  figures.json log.
Everything is deterministic and works offline. Placement can be corrected by editing figures.json
and re-applying it (`--figures-json`).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .align_content import _bigrams, _cosine
from .markup import strip as _strip
from .models import Figure, LectureNote, Statement, Topic
from .template import Template

IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
_CAP_START = re.compile(r"^\s*(Figure|Fig\.?|그림|Table|표|Source|출처)\b", re.I)


# ----------------------------------------------------------------------------- extraction
def _merge_rects(rects, gap=6.0):
    rects = [r for r in rects]
    changed = True
    while changed:
        changed = False
        out = []
        while rects:
            r = rects.pop()
            grown = type(r)(r.x0 - gap, r.y0 - gap, r.x1 + gap, r.y1 + gap)
            for i, o in enumerate(out):
                if grown.intersects(o):
                    out[i] = o | r
                    changed = True
                    break
            else:
                out.append(r)
        rects = out
    return rects


def _caption_for(rect, blocks) -> str:
    """Text block right below (<=45pt) or above (<=30pt) the figure, preferring 'Figure…/그림…' starts."""
    best = ""
    for b in blocks:
        x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], (b[4] or "").strip()
        if not text or b[6] != 0:  # 0 = text block
            continue
        horiz = min(x1, rect.x1) - max(x0, rect.x0)
        if horiz < 0.3 * min(x1 - x0, rect.width):
            continue
        below = 0 <= y0 - rect.y1 <= 45
        above = 0 <= rect.y0 - y1 <= 30
        one = " ".join(text.split())
        if (below or above) and len(one) <= 160:
            if _CAP_START.match(one):
                return one
            # a label-like phrase, not the author's explanatory sentence next to the figure
            if below and not best and len(one) <= 60 and not re.search(r"(다|요|죠|까|음|함)[.!?)]*$", one):
                best = one
    return best


def _near_text(rect, blocks, max_chars: int = 400) -> str:
    """Text that explains the figure: blocks BESIDE it (vertical overlap, <=260pt away) or directly
    above / below it (horizontal overlap, <=55pt). Farther headings of other sections are ignored."""
    scored = []
    for b in blocks:
        x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], " ".join((b[4] or "").split())
        if not text or b[6] != 0:
            continue
        v_overlap = min(y1, rect.y1) - max(y0, rect.y0)
        h_overlap = min(x1, rect.x1) - max(x0, rect.x0)
        dx = max(x0 - rect.x1, rect.x0 - x1, 0)
        dy = max(y0 - rect.y1, rect.y0 - y1, 0)
        if v_overlap > 8 and dx <= 260:
            scored.append((dx * 0.5, text))
        elif h_overlap > 8 and dy <= 55:
            scored.append((dy, text))
    return " ".join(t for _, t in sorted(scored))[:max_chars]


def looks_like_text_image(path: str | Path) -> bool:
    """Mostly black-on-white text (no colour, little ink): a bullet-point slide, not a figure."""
    from PIL import Image

    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((220, 220))
        px = list(im.getdata()) if not hasattr(im, "get_flattened_data") else list(im.get_flattened_data())
    n = len(px) or 1
    ink = sum(1 for r, g, b in px if (r + g + b) / 3 < 170) / n
    colour = sum(1 for r, g, b in px if max(r, g, b) - min(r, g, b) > 25) / n  # pastel diagrams still count
    return colour < 0.008 and ink < 0.2  # calibrated: bullet slides <= 0.005, faint line diagrams >= 0.010


def extract_pdf_figures(pdf: str | Path, out_dir: str | Path, start_id: int = 1, dpi: int = 170,
                        min_w_pt: float = 60, min_h_pt: float = 45, as_units: bool = False) -> list[Figure]:
    """Every sizeable picture on every page, rendered as a clip (keeps overlaid arrows/labels)."""
    import pymupdf

    pdf, out_dir = Path(pdf), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf))
    raw: list[tuple] = []
    for pno, page in enumerate(doc, start=1):
        pw, ph = page.rect.width, page.rect.height
        rects = []
        for info in page.get_image_info():
            r = pymupdf.Rect(info["bbox"]) & page.rect
            if r.is_empty or r.width < min_w_pt or r.height < min_h_pt:
                continue
            if r.width * r.height > 0.85 * pw * ph:  # full-page background
                continue
            rects.append(r)
        text = page.get_text("text")
        blocks = page.get_text("blocks")
        for rect in sorted(_merge_rects(rects), key=lambda r: (round(r.y0 / 20), r.x0)):
            scale = dpi / 72
            while rect.width * scale > 1500 or rect.height * scale > 1500:
                scale *= 0.85
            pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=rect, alpha=False)
            raw.append((pno, rect, pix.tobytes("png"), _caption_for(rect, blocks), text, pix.width, pix.height,
                        _near_text(rect, blocks)))
    # decorations (same picture on >= 3 pages, e.g. logos) and exact duplicates
    digest_pages: dict[str, set[int]] = {}
    for pno, _, data, *_ in raw:
        digest_pages.setdefault(hashlib.md5(data).hexdigest(), set()).add(pno)
    figs: list[Figure] = []
    seen: set[str] = set()
    for pno, rect, data, cap, text, w, h, near in raw:
        d = hashlib.md5(data).hexdigest()
        if len(digest_pages[d]) >= 3 or d in seen:
            continue
        seen.add(d)
        fid = start_id + len(figs)
        path = out_dir / f"{pdf.stem[:24]}_p{pno:02d}_{fid:03d}.png"
        path.write_bytes(data)
        figs.append(Figure(id=fid, path=str(path), source=pdf.name, page=pno, caption=cap,
                           text_like=looks_like_text_image(path) if not as_units else False,
                           context=" ".join(text.split())[:3000], near=near, width=w, height=h,
                           unit=pno if as_units else None))
    return figs


def extract_pdf_slides(pdf: str | Path, image_dir: str | Path):
    """Slide PDF -> (slides, figures): one unit per page (text) + its pictures as figures with unit=page."""
    import pymupdf

    from .models import BodyLine, Slide

    figs = extract_pdf_figures(pdf, image_dir, as_units=True)
    by_page: dict[int, list[Figure]] = {}
    for f in figs:
        by_page.setdefault(f.page, []).append(f)
    slides = []
    for pno, page in enumerate(pymupdf.open(str(pdf)), start=1):
        lines = [ln.strip() for ln in page.get_text("text").splitlines() if ln.strip()]
        title = lines[0][:80] if lines else ""
        slides.append(Slide(number=pno, title=title, body=[BodyLine(text=t) for t in lines[1:]],
                            images=[f.path for f in by_page.get(pno, [])]))
    return slides, figs


def slide_figures(slides, start_id: int = 1) -> list[Figure]:
    """Pictures that came with PPTX/PDF slides -> Figure objects bound to their slide (unit)."""
    figs: list[Figure] = []
    for s in slides:
        for p in s.images:
            figs.append(Figure(id=start_id + len(figs), path=p, source=f"slide {s.number}", page=s.number,
                               caption=s.title, context=s.plain_text()[:3000], unit=s.number))
    return figs


def extract_pptx_figures(pptx: str | Path, out_dir: str | Path, start_id: int = 1) -> list[Figure]:
    from .extract_slides import extract_pptx

    slides = extract_pptx(pptx, out_dir)
    figs = slide_figures(slides, start_id)
    for f in figs:
        f.source = Path(pptx).name
        f.unit = None  # figure source only: match by text, not by slide number
    return figs


def extract_images(files: list[Path], start_id: int = 1) -> list[Figure]:
    """Plain image files; the file name (underscores -> spaces) is both caption and matching text."""
    from PIL import Image

    figs: list[Figure] = []
    for p in files:
        with Image.open(p) as im:
            w, h = im.size
        name = p.stem.replace("_", " ").replace("-", " ")
        figs.append(Figure(id=start_id + len(figs), path=str(p), source=p.name, caption=name, context=name,
                           width=w, height=h))
    return figs


def extract_image_dir(folder: str | Path, start_id: int = 1) -> list[Figure]:
    return extract_images([p for p in sorted(Path(folder).iterdir()) if p.suffix.lower() in IMG_EXT], start_id)


def collect_figures(paths: list[str | Path], out_dir: str | Path) -> list[Figure]:
    out_dir = Path(out_dir)
    figs: list[Figure] = []
    for p in map(Path, paths):
        if p.is_dir():
            figs += extract_image_dir(p, len(figs) + 1)
        elif p.suffix.lower() == ".pdf":
            figs += extract_pdf_figures(p, out_dir, len(figs) + 1)
        elif p.suffix.lower() == ".pptx":
            figs += extract_pptx_figures(p, out_dir / (p.stem + "_raw"), len(figs) + 1)
        elif p.suffix.lower() in IMG_EXT:
            figs += extract_images([p], len(figs) + 1)
        else:
            raise ValueError(f"지원하지 않는 그림 자료 형식: {p}")
    for i, f in enumerate(figs, start=1):  # unique ids across sources
        f.id = i
    return figs


# ----------------------------------------------------------------------------- placement
def _rank(query: str, docs: list[str]) -> list[float]:
    """tf-idf cosine of `query` against each doc (idf over `docs`): distinctive bigrams decide, not common ones."""
    import math
    from collections import Counter

    dv = [_bigrams(d) for d in docs]
    df: Counter = Counter()
    for v in dv:
        df.update(v.keys())
    n = len(docs)
    idf = lambda k: math.log((n + 1) / (df.get(k, 0) + 1)) + 1.0
    w = lambda c: {k: v * idf(k) for k, v in c.items()}
    qv = w(_bigrams(query))
    qn = math.sqrt(sum(x * x for x in qv.values())) or 1.0
    out = []
    for c in dv:
        d = w(c)
        dn = math.sqrt(sum(x * x for x in d.values())) or 1.0
        out.append(sum(x * d.get(k, 0.0) for k, x in qv.items()) / (qn * dn))
    return out


def _topic_text(t: Topic) -> str:
    parts = [t.heading, t.chapter, t.basics_title, *[_strip(b) for b in t.basics]]
    for sts in t.sections.values():
        parts += [_strip(s.text) for s in sts if s.kind != "figure"]
    return " ".join(parts)


def _body_key(t: Topic, tpl: Template) -> str | None:
    for k in tpl.keys:
        if t.sections.get(k):
            return k
    return next(iter(t.sections), None)


def place_figures(note: LectureNote, figures: list[Figure], tpl: Template, max_per_topic: int = 6,
                  min_score: float = 0.10, soft_order_penalty: float = 0.12,
                  keep_text_images: bool = False) -> list[Figure]:
    """Decide topic + anchor for every figure, insert Statement(kind='figure') and return the log."""
    body_idx = [i for i, t in enumerate(note.topics) if t.role == "body"]
    if not body_idx or not figures:
        return figures
    tvec = {i: _bigrams(_topic_text(note.topics[i])) for i in body_idx}

    def topic_scores(f: Figure) -> dict[int, float]:
        """Plain bigram cosine (stable for long section texts): whole page + the text right next to the figure."""
        whole = _bigrams(f.context + " " + f.caption)
        near = _bigrams(f.near) if f.near else whole
        return {i: 0.4 * _cosine(whole, tvec[i]) + 0.6 * _cosine(near, tvec[i]) for i in body_idx}

    # 0. manual section choice by heading text
    for f in figures:
        if f.topic_heading and f.topic is None:
            hit = [i for i in body_idx if f.topic_heading in note.topics[i].heading]
            if hit:
                f.topic, f.score = hit[0], 1.0
    # 1. topic choice
    for f in figures:
        if f.skip or f.topic is not None or (f.text_like and not keep_text_images):
            continue
        if f.unit is not None:  # bound to a slide/page: the topic(s) citing that unit
            hits = [i for i in body_idx if f.unit in note.topics[i].slide_numbers]
            if hits:
                f.topic, f.score = hits[0], 1.0
                continue
    free = [f for f in figures if not f.skip and not (f.text_like and not keep_text_images) and f.topic is None]
    by_source: dict[str, list[Figure]] = {}
    for f in free:
        by_source.setdefault(f.source, []).append(f)
    for src, fs in by_source.items():
        fs.sort(key=lambda f: (f.page, f.id))
        # paged sources (PDF / slides / finished notes) follow the lecture order -> sections may not go
        # backwards; unordered sources (loose image folders) only get a soft preference
        order_penalty = 10.0 if all(f.page > 0 for f in fs) else soft_order_penalty
        sc = []
        for f in fs:
            sc.append(topic_scores(f))
        # DP: maximise sum(score) with a soft penalty when the topic order goes backwards
        n = len(fs)
        NEG = -1e9
        best = [{j: NEG for j in body_idx} for _ in range(n)]
        back = [{j: None for j in body_idx} for _ in range(n)]
        for j in body_idx:
            best[0][j] = sc[0][j]
        for k in range(1, n):
            for j in body_idx:
                cand = max(((best[k - 1][p] - (order_penalty if p > j else 0.0)), p) for p in body_idx)
                best[k][j] = cand[0] + sc[k][j]
                back[k][j] = cand[1]
        j = max(body_idx, key=lambda x: best[n - 1][x])
        for k in range(n - 1, -1, -1):
            if sc[k][j] >= min_score:
                fs[k].topic, fs[k].score = j, round(sc[k][j], 3)
            j = back[k][j] if back[k][j] is not None else j
    # 2. per-topic cap (keep the best matches)
    per: dict[int, list[Figure]] = {}
    for f in figures:
        if f.topic is not None and not f.skip and f.unit is None:
            per.setdefault(f.topic, []).append(f)
    count = {i: len(per.get(i, [])) for i in body_idx}
    for t_idx, fs in per.items():
        for f in sorted(fs, key=lambda x: -x.score)[max_per_topic:]:
            f.topic = None
            count[t_idx] -= 1
            ts = topic_scores(f)
            for j in sorted(body_idx, key=lambda i: -ts[i]):  # next best section with room
                s = ts[j]
                if s >= min_score and count[j] < max_per_topic:
                    f.topic, f.score = j, round(s, 3)
                    count[j] += 1
                    break
    # 3. anchors + insertion
    inserts: dict[int, list[tuple[int, Figure]]] = {}
    last_after: dict[int, int] = {}
    for f in sorted(figures, key=lambda x: (x.source, x.page, x.id)):
        if f.skip or f.topic is None or (f.text_like and not keep_text_images):
            continue
        t = note.topics[f.topic]
        key = _body_key(t, tpl)
        sts = t.sections.get(key, []) if key else []
        if f.after is None and f.anchor:
            for k, st in enumerate(sts):  # manual: block named by its sub-heading
                if st.kind == "star" and f.anchor in _strip(st.text):
                    j = k + 1
                    while j < len(sts) and sts[j].kind in ("figure",):
                        j += 1
                    while j + 1 < len(sts) and sts[j].kind == "bullet" and sts[j + 1].kind == "bullet":
                        j += 1
                    f.after = j if j < len(sts) and sts[j].kind != "star" else k
                    break
        if f.after is None:
            # anchor = start of the best-matching "★ block" (sub-heading + its text); blue PAD summaries are
            # left out of the block text because they mention many terms and would attract every figure
            blocks: list[list[int]] = []
            for k, st in enumerate(sts):
                if st.kind == "star" or not blocks:
                    blocks.append([])
                blocks[-1].append(k)
            btexts = [" ".join(_strip(sts[k].text) for k in b if sts[k].kind != "figure"
                               and "{b|" not in sts[k].text) for b in blocks]
            rk = _rank((f.near or f.context) + " " + f.caption, btexts) if blocks else []
            floor = last_after.get(f.topic, -1) if f.page > 0 else -1  # same topic: keep page order
            order = sorted(range(len(blocks)), key=lambda i: (-rk[i], i)) if blocks else []
            pos = []
            for i in order:
                b_ = blocks[i]
                body = [k for k in b_ if sts[k].kind not in ("star", "figure")]
                if not body:
                    k = b_[-1]
                else:  # after the first paragraph / bullet run of the block
                    k = body[0]
                    while k + 1 < len(sts) and sts[k].kind == "bullet" and sts[k + 1].kind == "bullet":
                        k += 1
                pos.append(k)
            ok = [k for k in pos if k >= floor] or pos
            f.after = ok[0] if ok else -1
        last_after[f.topic] = max(last_after.get(f.topic, -1), f.after)
        inserts.setdefault(f.topic, []).append((f.after, f))
    for t_idx, items in inserts.items():
        t = note.topics[t_idx]
        key = _body_key(t, tpl) or tpl.keys[0]
        sts = t.sections.setdefault(key, [])
        for after, f in sorted(items, key=lambda x: (x[0], x[1].page, x[1].id), reverse=True):
            anchor = sts[after] if 0 <= after < len(sts) else None
            cap = f.caption or f"{t.heading} 관련 자료"
            src = f"{f.source}" + (f" p.{f.page}" if f.page and f.unit is None else "")
            sts.insert(after + 1, Statement(
                text=f"{cap}  (출처: {src})" if f.unit is None else cap,
                kind="figure", image=f.path, origin="both",
                slide_refs=list(anchor.slide_refs) if anchor else list(t.slide_numbers[:1])))
    note.figures = figures
    return figures


def save_figures(figures: list[Figure], path: str | Path) -> Path:
    p = Path(path)
    data = [f.model_dump(exclude={"context", "near"}) | {"near": f.near[:120]} for f in figures]
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def apply_overrides(figures: list[Figure], path: str | Path) -> None:
    """figures.json edited by hand: set `skip`, `topic`, `after`, `caption` per figure id."""
    edits = {e["id"]: e for e in json.loads(Path(path).read_text(encoding="utf-8"))}
    for f in figures:
        e = edits.get(f.id)
        if not e:
            continue
        f.skip = bool(e.get("skip", False))
        if e.get("topic") is not None and not e.get("topic_heading"):
            f.topic, f.score = e["topic"], max(f.score, 1.0)  # manual choice beats the automatic cap
        if e.get("after") is not None:
            f.after = e["after"]
        if e.get("caption"):
            f.caption = e["caption"]
        f.topic_heading = e.get("topic_heading", f.topic_heading)
        f.anchor = e.get("anchor", f.anchor)
        if "text_like" in e:
            f.text_like = bool(e["text_like"])
