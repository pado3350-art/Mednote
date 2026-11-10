"""Compare a generated note PDF with a human-written MOM note and list what is still unlike it (the "MOM closeness loop").

Measured (nothing is guessed):
  * pages, characters, characters per page, median glyph height (pt)          - density / readability
  * per page: FILL (how far down the content reaches, 0-1) and INK (% dark pixels) - empty pages, crowded pages
  * the ending style of table-cell lines in the generated note (note.json)     - 개조식 vs full '-다' sentences (rule L19)
`assess()` is pure (dicts in, findings out) so the thresholds are testable; `compare()` collects the numbers.
Usage:  python -m app.cli compare-mom MOM.pdf OURS.pdf [--note outputs/x/note.json] [--out report.md]
The MOM file is read here for COMPARISON only; generating a note must never read its text (pictures only).
Procedure and the findings so far: .claude/skills/mom-closeness-loop/
"""
from __future__ import annotations

import json
import re
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

# --------------------------------------------------------------------------- thresholds (relative to the MOM note)
MAX_PAGE_RATIO = 1.15  # ours may have at most 15% more pages
MAX_CHAR_RATIO = 1.20  # ... and 20% more characters per page (crowding)
MIN_CHAR_RATIO = 0.70  # ... but not far fewer (empty pages)
MIN_GLYPH_GAP_PT = 1.0  # text may be at most 1 pt smaller than the MOM's
MIN_PAGE_FILL = 0.6  # a page (except the last) whose content ends above 60% of the page is "half empty"
MAX_INK_RATIO = 1.30  # the most crowded page may be 30% inkier than the MOM's most crowded page
FILL_TOP_SKIP = 0.07  # ignore the page-number line at the very top


def _need(tool: str) -> str:
    exe = shutil.which(tool)
    if not exe:
        raise RuntimeError(f"{tool} 가 필요합니다 (poppler-utils)")
    return exe


# --------------------------------------------------------------------------- measurements
def page_metrics(pdf: str | Path, dpi: int = 40) -> list[dict]:
    """Per page: fill (last content row / page height) and ink (% of dark pixels)."""
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([_need("pdftoppm"), "-r", str(dpi), "-png", str(pdf), f"{tmp}/p"], check=True, capture_output=True)
        for f in sorted(Path(tmp).glob("p-*.png")):
            im = Image.open(f).convert("L")
            w, h = im.size
            ink = sum(im.histogram()[:200]) / (w * h)
            body = im.crop((0, int(h * FILL_TOP_SKIP), w, h)).point(lambda v: 255 if v < 235 else 0)
            box = body.getbbox()
            fill = (box[3] + int(h * FILL_TOP_SKIP)) / h if box else 0.0
            out.append({"fill": round(fill, 2), "ink": round(ink * 100, 1)})
    return out


def text_metrics(pdf: str | Path) -> dict:
    """Characters (without spaces) and the median glyph height in points."""
    text = subprocess.run([_need("pdftotext"), str(pdf), "-"], capture_output=True, text=True).stdout
    box = subprocess.run([_need("pdftotext"), "-bbox", str(pdf), "-"], capture_output=True, text=True).stdout
    heights = [float(b) - float(a) for a, b in re.findall(r'yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)"', box)]
    return {"chars": len(re.sub(r"\s", "", text)), "glyph_pt": round(statistics.median(heights), 1) if heights else 0.0}


def ending_kind(line: str) -> str:
    """How a Korean line ends: 합니다체 / 한다체(-다) / 개조식(-음,-함,-됨) / 명사·어간 / 영문·숫자."""
    s = re.sub(r"[\)\]\"'”’. ]+$", "", line.strip())
    if re.search(r"(습니다|입니다|니다)$", s):
        return "합니다체"
    if re.search(r"[가-힣]다$", s):
        return "한다체(-다)"
    if re.search(r"[가-힣](함|음|됨|임|킴|줌)$", s):
        return "개조식(-함/-음)"
    if re.search(r"[가-힣]$", s):
        return "명사·어간 종결"
    return "영문·숫자 종결"


def cell_lines(note_json: str | Path) -> list[str]:
    """Every line of every `rows` table cell (label column excluded), markup removed."""
    note = json.loads(Path(note_json).read_text(encoding="utf-8"))
    lines = []
    for t in note.get("topics", []):
        for sts in t.get("sections", {}).values():
            for st in sts:
                if st.get("kind") != "rows":
                    continue
                for row in st.get("rows", []):
                    for cell in row[1:]:
                        for ln in cell.split("\n"):
                            ln = re.sub(r"\{[a-z]\|([^}]*)\}", r"\1", ln).replace("**", "").strip()
                            if ln:
                                lines.append(ln)
    return lines


def note_shape(note_json: str | Path) -> dict:
    """Heading lengths, checks without a past-exam item (rule L20) - from note.json."""
    note = json.loads(Path(note_json).read_text(encoding="utf-8"))
    body = [t for t in note.get("topics", []) if t.get("role") == "body" and not t.get("heading", "").upper().startswith("QUIZ")]
    checks_no_pad = 0
    for t in body:
        sts = [s for v in t.get("sections", {}).values() for s in v]
        if any(s.get("kind") == "check" for s in sts) and not (
                any(r >= 1000 for s in sts for r in s.get("slide_refs", [])) or any(r >= 1000 for r in t.get("basics_refs", []))):
            checks_no_pad += 1
    return {"max_heading": max((len(t["heading"]) for t in body), default=0),
            "max_chapter": max((len(t.get("chapter", "")) for t in body), default=0),
            "checks": sum(1 for t in body for v in t.get("sections", {}).values() for s in v if s.get("kind") == "check"),
            "checks_without_pad": checks_no_pad}


# --------------------------------------------------------------------------- assessment (pure)
def summarize(pages: list[dict], text: dict) -> dict:
    n = len(pages)
    fills = [p["fill"] for p in pages]
    return {"pages": n, "chars": text["chars"], "chars_per_page": round(text["chars"] / n) if n else 0,
            "glyph_pt": text["glyph_pt"], "avg_fill": round(statistics.mean(fills), 2) if fills else 0.0,
            "half_empty": [i + 1 for i, f in enumerate(fills[:-1]) if f < MIN_PAGE_FILL],
            "max_ink": max((p["ink"] for p in pages), default=0.0), "fills": fills, "inks": [p["ink"] for p in pages]}


def assess(mom: dict, ours: dict, cells: list[str] | None = None, shape: dict | None = None) -> list[str]:
    """What is still unlike the MOM note. Empty list = nothing left that the measurements can see."""
    f: list[str] = []
    if mom["pages"] and ours["pages"] > mom["pages"] * MAX_PAGE_RATIO:
        f.append(f"쪽수 {ours['pages']}쪽 > MOM {mom['pages']}쪽의 {MAX_PAGE_RATIO:.2f}배: 반복 장치(Check, QUIZ, 중복 표현)와 새 쪽 강제를 줄인다")
    if mom["chars_per_page"]:
        r = ours["chars_per_page"] / mom["chars_per_page"]
        if r > MAX_CHAR_RATIO:
            f.append(f"쪽당 글자 {ours['chars_per_page']}자 = MOM의 {r:.2f}배: 표 칸 풀이와 문단을 줄인다(빽빽함)")
        elif r < MIN_CHAR_RATIO:
            f.append(f"쪽당 글자 {ours['chars_per_page']}자 = MOM의 {r:.2f}배: 쪽이 비었다")
    if ours["glyph_pt"] and mom["glyph_pt"] and ours["glyph_pt"] < mom["glyph_pt"] - MIN_GLYPH_GAP_PT:
        f.append(f"글자 크기 {ours['glyph_pt']}pt < MOM {mom['glyph_pt']}pt: 본문·표 글자를 키운다(템플릿 font_size_pt)")
    if ours["half_empty"]:
        f.append(f"절반 이하로 비는 쪽(마지막 쪽 제외): {ours['half_empty']} → 이어 붙이기·새 쪽 강제(new_page) 조정")
    if mom["max_ink"] and ours["max_ink"] > mom["max_ink"] * MAX_INK_RATIO:
        worst = ours["inks"].index(ours["max_ink"]) + 1
        f.append(f"{worst}쪽 잉크 {ours['max_ink']}% > MOM 최대 {mom['max_ink']}%의 {MAX_INK_RATIO:.1f}배: 그 쪽을 둘로 나눈다")
    if cells:
        bad = [c for c in cells if ending_kind(c) == "한다체(-다)"]
        if bad:
            f.append(f"표 칸 {len(bad)}/{len(cells)}줄이 ‘-다’ 문장: 개조식(명사형, ‘-음/-함’)으로(L19) 예: {bad[0][:30]}")
    if shape:
        if shape["max_heading"] > 44 or shape["max_chapter"] > 34:
            f.append(f"제목 길이 소절 {shape['max_heading']}자 / 장 {shape['max_chapter']}자(한계 44 / 34): 한 줄로 줄인다")
        if shape["checks_without_pad"]:
            f.append(f"기출이 없는 소절 {shape['checks_without_pad']}곳에 개념 Check(L20): 뺀다")
    return f


def compare(mom_pdf: str | Path, our_pdf: str | Path, note_json: str | Path | None = None) -> dict:
    mom = summarize(page_metrics(mom_pdf), text_metrics(mom_pdf))
    ours = summarize(page_metrics(our_pdf), text_metrics(our_pdf))
    cells = cell_lines(note_json) if note_json else None
    shape = note_shape(note_json) if note_json else None
    return {"mom": mom, "ours": ours, "cells": {k: sum(1 for c in cells if ending_kind(c) == k) for k in
                                                   ("한다체(-다)", "개조식(-함/-음)", "명사·어간 종결", "영문·숫자 종결")} if cells else None,
            "shape": shape, "findings": assess(mom, ours, cells, shape)}


def format_report(r: dict) -> str:
    m, o = r["mom"], r["ours"]
    L = ["# MOM 근접도 측정", "", "| | MOM | 생성본 |", "|---|---|---|",
         f"| 쪽수 | {m['pages']} | {o['pages']} |", f"| 쪽당 글자 | {m['chars_per_page']} | {o['chars_per_page']} |",
         f"| 글자 크기(중앙값) | {m['glyph_pt']} pt | {o['glyph_pt']} pt |", f"| 쪽 평균 채움 | {m['avg_fill']} | {o['avg_fill']} |",
         f"| 가장 빽빽한 쪽의 잉크 | {m['max_ink']}% | {o['max_ink']}% |", f"| 절반 이하로 빈 쪽 | {m['half_empty']} | {o['half_empty']} |"]
    if r.get("cells"):
        L += ["", "표 칸 줄의 끝맺음(생성본): " + ", ".join(f"{k} {v}" for k, v in r["cells"].items())]
    if r.get("shape"):
        s = r["shape"]
        L += [f"제목 최대 길이: 소절 {s['max_heading']}자, 장 {s['max_chapter']}자 · 개념 Check {s['checks']}개(기출 없는 소절 {s['checks_without_pad']}곳)"]
    L += ["", "## 남은 차이" if r["findings"] else "## 남은 차이: 측정으로 보이는 것은 없음"]
    L += [f"- {x}" for x in r["findings"]]
    return "\n".join(L) + "\n"
