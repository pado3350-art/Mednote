"""CLI:  python -m app.cli build lecture.pptx --script lecture.txt --out outputs/"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generate_notes import AnthropicBackend, OfflineBackend, PrecomputedBackend
from .pipeline import run_pipeline

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "medical.yaml"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mednote")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="PPTX (+ script) -> DOCX/MD lecture note")
    b.add_argument("pptx", nargs="?", help="PPTX (optional if the script has [mm:ss–mm:ss] block headers)")
    b.add_argument("--script", help="TXT/DOCX lecture script")
    b.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    b.add_argument("--out", default="outputs")
    b.add_argument("--title")
    b.add_argument("--backend", choices=["offline", "anthropic"], default="offline")
    b.add_argument("--model")
    b.add_argument("--note-json", help="use pre-authored topics (note.json) instead of a backend")
    b.add_argument("--date", help="YYYY-MM-DD")
    b.add_argument("--subject")
    b.add_argument("--professor")
    b.add_argument("--author")
    b.add_argument("--comment", help="작성자 코멘트 (use \\n for new lines)")
    b.add_argument("--exam-pdf", help="PAD(기출문제) PDF; 파랑 글씨는 여기 나온 내용에만 허용")
    b.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args(argv)
    if not a.pptx and not a.script:
        ap.error("pptx 또는 --script 필요")

    if a.note_json:
        backend = PrecomputedBackend.from_json(a.note_json)
    else:
        backend = OfflineBackend() if a.backend == "offline" else AnthropicBackend(model=a.model)
    meta = {k: v for k in ("date", "subject", "professor", "author") if (v := getattr(a, k))}
    if a.comment:
        meta["comment"] = a.comment.replace("\\n", "\n")
    report, paths = run_pipeline(a.pptx, a.out, a.template, a.script, backend, a.title, meta, pdf=not a.no_pdf, exam_pdf=a.exam_pdf)
    for k, v in paths.items():
        print(f"{k:12s} {v}")
    print(f"coverage {report.slide_coverage:.0%}  errors {len(report.errors)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
