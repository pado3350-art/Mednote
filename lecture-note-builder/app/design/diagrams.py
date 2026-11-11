"""Schematics drawn by the program (PIL, no external service): concept tree, left-to-right flow, comparison cards.

Text inside boxes uses the note markup, so colours follow the same rules as the body text:
red = lecturer emphasis, BLUE = PAD (기출) only, gray = low importance, purple = needs checking, **bold** = key term.
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..markup import runs
from ..models import Diagram

W = 1700  # canvas width in px (placed at ~16.5 cm -> ~260 dpi); "side" diagrams use SIDE_W
SIDE_W = 900  # narrow canvas for diagrams placed beside text (~7 cm wide)
M = 40  # outer margin
INK = (30, 30, 30)
TEXT_COLORS = {None: INK, "emphasis": (192, 0, 0), "exam": (31, 78, 200), "exam_other": (0, 150, 205), "minor": (130, 130, 130),
               "verify": (112, 48, 160), "highlight": INK, "underline": INK, "dots": INK, "key": (192, 0, 0)}
PALETTE = {"teal": (31, 138, 122), "blue": (47, 95, 179), "salmon": (230, 80, 90), "amber": (200, 130, 20),
           "violet": (112, 48, 160), "gray": (100, 100, 100), "green": (60, 140, 80)}
CYCLE = ["teal", "blue", "salmon", "amber", "violet", "green"]
FONT_CANDIDATES = [
    os.environ.get("MEDNOTE_FONT", ""),
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "/usr/share/fonts/truetype/unifont/unifont.ttf",
    "C:/Windows/Fonts/malgun.ttf", "/System/Library/Fonts/AppleSDGothicNeo.ttc", "/Library/Fonts/AppleGothic.ttf",
]
_cache: dict[int, ImageFont.FreeTypeFont] = {}


def font(size: int):
    if size not in _cache:
        for p in FONT_CANDIDATES:
            if p and Path(p).exists():
                try:
                    _cache[size] = ImageFont.truetype(p, size)
                    break
                except OSError:
                    continue
        else:
            _cache[size] = ImageFont.load_default()
    return _cache[size]


# ------------------------------------------------------------------ text layout
Seg = tuple[str, tuple[int, int, int], bool]  # (text, colour, bold)


def _tokens(text: str) -> list[Seg]:
    out: list[Seg] = []
    for t, col, bold in runs(text):
        parts = t.replace("\n", " ").split(" ")
        for i, w in enumerate(parts):
            if w or i == 0:
                out.append((w + (" " if i < len(parts) - 1 else ""), TEXT_COLORS[col], bool(bold)))
    return out


def wrap(text: str, size: int, max_w: int) -> list[list[Seg]]:
    f = font(size)
    lines: list[list[Seg]] = [[]]
    x = 0.0
    for tok, col, bold in _tokens(text):
        pieces = [tok]
        if f.getlength(tok) > max_w:  # a long unbroken word: split by characters
            pieces, cur = [], ""
            for ch in tok:
                if f.getlength(cur + ch) > max_w and cur:
                    pieces.append(cur); cur = ch
                else:
                    cur += ch
            pieces.append(cur)
        for k, p in enumerate(pieces):
            w = f.getlength(p)
            if (x + w > max_w and lines[-1] and p.strip()) or k > 0:
                lines.append([]); x = 0.0
            lines[-1].append((p, col, bold))
            x += w
    return [ln for ln in lines if ln]


def draw_lines(d: ImageDraw.ImageDraw, lines: list[list[Seg]], x: int, y: int, size: int, lh: float = 1.32) -> int:
    f = font(size)
    for ln in lines:
        cx = x
        for text, col, bold in ln:
            d.text((cx, y), text, font=f, fill=col, stroke_width=1 if bold else 0, stroke_fill=col)
            cx += f.getlength(text)
        y += int(size * lh)
    return y


def block_height(lines: list[list[Seg]], size: int, lh: float = 1.32) -> int:
    return int(len(lines) * size * lh)


def _items_layout(items: list[str], size: int, max_w: int):
    """bullets with hanging indent -> [(lines, indent_px)]"""
    bw = int(size * 0.95)  # bullets are drawn as dots (not every font has the glyph)
    return [(wrap(it, size, max_w - bw), bw) for it in items]


def _items_height(laid, size: int, gap: int = 8) -> int:
    return sum(block_height(ls, size) + gap for ls, _ in laid)


def _draw_items(d, laid, x: int, y: int, size: int, gap: int = 8) -> int:
    for lines, bw in laid:
        r = max(4, size // 7)
        cy = y + int(size * 0.62)
        d.ellipse((x + 2, cy - r, x + 2 + 2 * r, cy + r), fill=(70, 70, 70))
        y = draw_lines(d, lines, x + bw, y, size) + gap
    return y


def _tint(c, a=0.9):
    return tuple(int(255 - (255 - v) * (1 - a)) for v in c)


def _color(g, i):
    return PALETTE.get(g.color or CYCLE[i % len(CYCLE)], PALETTE["teal"])


def _arrow(d, p0, p1, color, width=5, head=18):
    import math
    d.line([p0, p1], fill=color, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.45, 0.45):
        d.line([p1, (p1[0] - head * math.cos(ang + s), p1[1] - head * math.sin(ang + s))], fill=color, width=width)


def _card(d, x, y, w, h, color, title, laid, tsize, isize, title_lines):
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=_tint(color, 0.93), outline=color, width=3)
    th = block_height(title_lines, tsize) + 22
    d.rounded_rectangle((x, y, x + w, y + th), radius=16, fill=color)
    d.rectangle((x, y + th - 16, x + w, y + th), fill=color)
    draw_lines_white(d, title_lines, x + 18, y + 11, tsize)
    _draw_items(d, laid, x + 18, y + th + 14, isize)


def draw_lines_white(d, lines, x, y, size):
    f = font(size)
    for ln in lines:
        cx = x
        for text, _, _ in ln:
            d.text((cx, y), text, font=f, fill=(255, 255, 255), stroke_width=1, stroke_fill=(255, 255, 255))
            cx += f.getlength(text)
        y += int(size * 1.3)


# ------------------------------------------------------------------ layouts
def _title_h(spec: Diagram) -> tuple[list, int]:
    if not spec.title:
        return [], 0
    ls = wrap("**" + spec.title + "**", 40, W - 2 * M)
    return ls, block_height(ls, 40) + 26


def render_tree(spec: Diagram) -> Image.Image:
    n = max(len(spec.groups), 1)
    cols = n if n <= 4 else (n + 1) // 2
    cw = (W - 2 * M - 70 - 28 * (cols - 1)) // cols
    tsize, isize = 34, 30
    tl, th0 = _title_h(spec)
    root_lines = wrap("**" + spec.root + "**", 40, int(W * 0.55))
    rh = block_height(root_lines, 40) + 36
    cards = []
    for i, g in enumerate(spec.groups):
        tl2 = wrap("**" + g.title + "**", tsize, cw - 36)
        laid = _items_layout(g.items, isize, cw - 36)
        h = block_height(tl2, tsize, 1.3) + 22 + _items_height(laid, isize) + 30
        cards.append((g, tl2, laid, h))
    rows = [cards[r * cols:(r + 1) * cols] for r in range((n + cols - 1) // cols)]
    row_h = [max(c[3] for c in r) for r in rows]
    gap_y = 70
    H = M + th0 + rh + gap_y + sum(row_h) + gap_y * (len(rows) - 1) + M
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    y = M
    if tl:
        draw_lines(d, tl, M, y, 40); y += th0
    rw = max(int(max((sum(font(40).getlength(t) for t, _, _ in ln) for ln in root_lines), default=300)) + 80, 380)
    rx = (W - rw) // 2
    d.rounded_rectangle((rx, y, rx + rw, y + rh), radius=22, fill=(40, 40, 40))
    draw_lines_white(d, root_lines, rx + 35, y + 16, 40)
    spine_x = M // 2 + 6
    root_mid = y + rh // 2
    y += rh + gap_y
    bus_ys, cy = [], y
    for r, rh_ in zip(rows, row_h):
        bus_ys.append(cy - gap_y // 2)
        for k, (g, tl2, laid, h) in enumerate(r):
            x = M + 35 + k * (cw + 28)
            c = _color(g, rows.index(r) * cols + k)
            _card(d, x, cy, cw, rh_, c, g.title, laid, tsize, isize, tl2)
            d.line([(x + cw // 2, cy), (x + cw // 2, bus_ys[-1])], fill=(90, 90, 90), width=4)
        last_x = M + 35 + (len(r) - 1) * (cw + 28) + cw // 2
        d.line([(spine_x, bus_ys[-1]), (last_x, bus_ys[-1])], fill=(90, 90, 90), width=4)
        cy += rh_ + gap_y
    d.line([(rx, root_mid), (spine_x, root_mid)], fill=(90, 90, 90), width=4)
    d.line([(spine_x, root_mid), (spine_x, bus_ys[-1])], fill=(90, 90, 90), width=4)
    return im


def render_flow(spec: Diagram) -> Image.Image:
    n = max(len(spec.groups), 1)
    lab_w = max((font(26).getlength(a.label) for a in spec.arrows if abs(a.src - a.dst) == 1 and a.label), default=0)
    gap = int(max(120, lab_w + 44))  # room for the arrow label between two boxes
    cw = (W - 2 * M - gap * (n - 1)) // n
    tsize, isize = (34, 29) if n <= 4 else (30, 26)
    tl, th0 = _title_h(spec)
    cards = []
    for g in spec.groups:
        tl2 = wrap("**" + g.title + "**", tsize, cw - 30)
        laid = _items_layout(g.items, isize, cw - 30)
        cards.append((g, tl2, laid, block_height(tl2, tsize, 1.3) + 22 + _items_height(laid, isize) + 30))
    hh = max(c[3] for c in cards)
    top_space = 70 if any(abs(a.src - a.dst) > 1 for a in spec.arrows) else 40
    H = M + th0 + top_space + hh + M
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    if tl:
        draw_lines(d, tl, M, M, 40)
    y0 = M + th0 + top_space
    xs = []
    for i, (g, tl2, laid, h) in enumerate(cards):
        x = M + i * (cw + gap)
        xs.append(x)
        _card(d, x, y0, cw, hh, _color(g, i), g.title, laid, tsize, isize, tl2)
    f = font(26)
    for a in spec.arrows:
        if not (0 <= a.src < n and 0 <= a.dst < n) or a.src == a.dst:
            continue
        col = (60, 60, 60)
        if abs(a.src - a.dst) == 1:
            s, t = (a.src, a.dst)
            x0 = xs[s] + (cw if t > s else 0) + (6 if t > s else -6)
            x1 = xs[t] + (0 if t > s else cw) + (-6 if t > s else 6)
            ym = y0 + hh // 2
            _arrow(d, (x0, ym), (x1, ym), col)
            if a.both:
                _arrow(d, (x1, ym), (x0, ym), col)
            if a.label:
                lw = f.getlength(a.label)
                d.text(((x0 + x1) / 2 - lw / 2, ym - 40), a.label, font=f, fill=col)
        else:  # skip arrow routed above the cards
            xa, xb = xs[a.src] + cw // 2, xs[a.dst] + cw // 2
            yt = y0 - 38
            d.line([(xa, y0), (xa, yt), (xb, yt)], fill=col, width=5)
            _arrow(d, (xb, yt), (xb, y0 - 4), col)
            if a.label:
                lw = f.getlength(a.label)
                d.text(((xa + xb) / 2 - lw / 2, yt - 34), a.label, font=f, fill=col)
    return im


def render_compare(spec: Diagram) -> Image.Image:
    ncol = max(len(spec.groups), 1)
    nrow = max((len(g.items) for g in spec.groups), default=0)
    label_w = 0
    isize, tsize = 28, 34
    if spec.row_labels:
        label_w = int(max(font(isize).getlength(t) for t in spec.row_labels)) + 50
        label_w = min(max(label_w, 160), 380)
    cw = (W - 2 * M - label_w) // ncol
    tl, th0 = _title_h(spec)
    head = [wrap("**" + g.title + "**", tsize, cw - 30) for g in spec.groups]
    hh = max(block_height(h, tsize, 1.3) for h in head) + 28
    rows_h = []
    cells = []
    for r in range(nrow):
        row_cells = []
        for g in spec.groups:
            txt = g.items[r] if r < len(g.items) else ""
            row_cells.append(wrap(txt, isize, cw - 30) if txt else [])
        lab = wrap("**" + spec.row_labels[r] + "**", isize, label_w - 28) if spec.row_labels and r < len(spec.row_labels) else []
        cells.append((lab, row_cells))
        rows_h.append(max([block_height(c, isize) for c in row_cells] + [block_height(lab, isize)]) + 26)
    H = M + th0 + hh + sum(rows_h) + M
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    if tl:
        draw_lines(d, tl, M, M, 40)
    y = M + th0
    for i, g in enumerate(spec.groups):
        x = M + label_w + i * cw
        c = _color(g, i)
        d.rectangle((x, y, x + cw, y + hh), fill=c, outline="white", width=3)
        draw_lines_white(d, head[i], x + 15, y + 14, tsize)
    y += hh
    for r, (lab, row_cells) in enumerate(cells):
        h = rows_h[r]
        if label_w:
            d.rectangle((M, y, M + label_w, y + h), fill=(236, 236, 236), outline=(190, 190, 190), width=2)
            draw_lines(d, lab, M + 14, y + 13, isize)
        for i, c in enumerate(row_cells):
            x = M + label_w + i * cw
            d.rectangle((x, y, x + cw, y + h), fill=_tint(_color(spec.groups[i], i), 0.94) if r % 2 == 0 else "white",
                        outline=(190, 190, 190), width=2)
            draw_lines(d, c, x + 15, y + 13, isize)
        y += h
    return im


def render_pyramid(spec: Diagram) -> Image.Image:
    """Hierarchy drawn as stacked trapezoid bands: groups[0] = top (narrowest, highest level) ... last = base.
    `root` is written along an upward arrow on the left (e.g. "분화능 ↑")."""
    n = max(len(spec.groups), 1)
    tsize, isize = (38, 30) if W <= SIDE_W else (40, 32)
    tl, th0 = _title_h(spec)
    axis = 110 if spec.root else 0
    x0, x1 = M + axis, W - M
    full = x1 - x0
    cx = (x0 + x1) // 2
    w_top, w_bot = int(full * 0.42), full
    bands = []
    for i, g in enumerate(spec.groups):
        wt = w_top + (w_bot - w_top) * i // n
        inner = int(wt * 0.86) - 40
        tl2 = wrap("**" + g.title + "**", tsize, inner)
        il = [wrap(it, isize, inner) for it in g.items]
        h = block_height(tl2, tsize, 1.25) + sum(block_height(x, isize, 1.25) for x in il) + 44
        bands.append((g, tl2, il, h))
    H = M + th0 + sum(b[3] for b in bands) + M
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    if tl:
        draw_lines(d, tl, M, M, 40)
    y = M + th0
    for i, (g, tl2, il, h) in enumerate(bands):
        wt = w_top + (w_bot - w_top) * i // n
        wb = w_top + (w_bot - w_top) * (i + 1) // n
        c = _color(g, i)
        d.polygon([(cx - wt // 2, y), (cx + wt // 2, y), (cx + wb // 2, y + h), (cx - wb // 2, y + h)],
                  fill=c, outline="white")
        d.line([(cx - wb // 2, y + h), (cx + wb // 2, y + h)], fill="white", width=4)
        yy = y + 20
        for ln in tl2:
            lw = sum(font(tsize).getlength(t) for t, _, _ in ln)
            draw_lines_white(d, [ln], int(cx - lw / 2), yy, tsize); yy += int(tsize * 1.25)
        for lines in il:
            for ln in lines:
                lw = sum(font(isize).getlength(t) for t, _, _ in ln)
                f = font(isize); xx = cx - lw / 2
                for text, _, bold in ln:
                    d.text((xx, yy), text, font=f, fill=(255, 255, 255), stroke_width=1 if bold else 0, stroke_fill=(255, 255, 255))
                    xx += f.getlength(text)
                yy += int(isize * 1.25)
        y += h
    if spec.root:  # upward axis arrow with its label
        ax = M + 30
        _arrow(d, (ax, M + th0 + sum(b[3] for b in bands) - 10), (ax, M + th0 + 10), (70, 70, 70), width=6, head=24)
        chars = [ch for ch in spec.root.replace("↑", "").replace(" ", "")]  # stacked vertical label (reads in Korean)
        f = font(32)
        total = len(chars) * 38
        yy = M + th0 + (sum(b[3] for b in bands) - total) // 2
        for ch in chars:
            d.text((ax + 22, yy), ch, font=f, fill=(70, 70, 70)); yy += 38
    return im


def render_cycle(spec: Diagram) -> Image.Image:
    """Loop: groups around a circle, arrows i -> i+1 and last -> first; `root` in the middle."""
    import math

    n = max(len(spec.groups), 2)
    tsize, isize = (34, 28)
    tl, th0 = _title_h(spec)
    cw = int(W * (0.36 if n <= 3 else 0.30))
    cards = []
    for g in spec.groups:
        tl2 = wrap("**" + g.title + "**", tsize, cw - 36)
        laid = _items_layout(g.items, isize, cw - 36)
        cards.append((g, tl2, laid, block_height(tl2, tsize, 1.3) + 22 + _items_height(laid, isize) + 26))
    ch = max(c[3] for c in cards)
    rx = (W - 2 * M - cw) / 2
    ry = max(ch * 1.3, rx * (0.7 if n <= 3 else 0.85))
    H = int(M + th0 + 2 * ry + ch + M)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    if tl:
        draw_lines(d, tl, M, M, 40)
    ccx, ccy = W / 2, M + th0 + ch / 2 + ry
    pos = []
    for i in range(len(cards)):
        a = -math.pi / 2 + 2 * math.pi * i / len(cards)
        pos.append((ccx + rx * math.cos(a), ccy + ry * math.sin(a)))
    boxes = []
    for i, ((g, tl2, laid, h), (px, py)) in enumerate(zip(cards, pos)):
        x, y = int(px - cw / 2), int(py - ch / 2)
        boxes.append((x, y, x + cw, y + ch))
    col = (70, 70, 70)

    def edge(b, tx, ty):  # point where the line from the box centre to (tx, ty) leaves the box
        bx, by = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        dx, dy = tx - bx, ty - by
        sx = (b[2] - b[0]) / 2 / abs(dx) if dx else 1e9
        sy = (b[3] - b[1]) / 2 / abs(dy) if dy else 1e9
        k = min(sx, sy)
        return bx + dx * k, by + dy * k

    for i in range(len(boxes)):
        j = (i + 1) % len(boxes)
        bi, bj = boxes[i], boxes[j]
        ci = ((bi[0] + bi[2]) / 2, (bi[1] + bi[3]) / 2)
        cj = ((bj[0] + bj[2]) / 2, (bj[1] + bj[3]) / 2)
        p0, p1 = edge(bi, *cj), edge(bj, *ci)
        v = (p1[0] - p0[0], p1[1] - p0[1]); L = math.hypot(*v) or 1
        p0 = (p0[0] + v[0] / L * 14, p0[1] + v[1] / L * 14); p1 = (p1[0] - v[0] / L * 14, p1[1] - v[1] / L * 14)
        _arrow(d, p0, p1, col, width=6, head=24)
        lab = next((a.label for a in spec.arrows if a.src == i and a.dst == j and a.label), "")
        if lab:
            f = font(26); lw = f.getlength(lab)
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            # push the label outwards, away from the centre
            ox, oy = mx - ccx, my - ccy; OL = math.hypot(ox, oy) or 1
            d.text((mx + ox / OL * 30 - lw / 2, my + oy / OL * 30 - 15), lab, font=f, fill=col)
    for (g, tl2, laid, h), b, i in zip(cards, boxes, range(len(cards))):
        _card(d, b[0], b[1], cw, ch, _color(g, i), g.title, laid, tsize, isize, tl2)
    if spec.root:
        rl = wrap("**" + spec.root + "**", 32, int(rx * 0.9))
        y = int(ccy - block_height(rl, 32) / 2)
        for ln in rl:
            lw = sum(font(32).getlength(t) for t, _, _ in ln)
            draw_lines(d, [ln], int(ccx - lw / 2), y, 32); y += int(32 * 1.32)
    return im


def render_diagram(spec: Diagram, path: str | Path) -> Path:
    global W
    old = W
    if spec.size == "side":
        W = SIDE_W
    try:
        im = {"tree": render_tree, "flow": render_flow, "compare": render_compare,
              "pyramid": render_pyramid, "cycle": render_cycle}[spec.kind](spec)
    finally:
        W = old
    if spec.kind == "cycle":  # trim the unused band under the lower cards
        from PIL import ImageChops

        box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        if box:
            im = im.crop((0, max(0, box[1] - M), im.width, min(im.height, box[3] + M)))
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p)
    return p


def diagram_texts(spec: Diagram) -> list[str]:
    out = [spec.root, spec.title, *spec.row_labels]
    for g in spec.groups:
        out += [g.title, *g.items]
    out += [a.label for a in spec.arrows]
    return [t for t in out if t]


def diagram_has_exam(spec: Diagram) -> bool:
    return any(c in ("exam", "exam_other") for t in diagram_texts(spec) for _, c, _ in runs(t))
