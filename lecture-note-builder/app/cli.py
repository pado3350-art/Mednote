"""CLI:  python -m app.cli build lecture.pptx --script lecture.txt --out outputs/"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generate_notes import AnthropicBackend, OfflineBackend
from .pipeline import run_pipeline

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "medical.yaml"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mednote")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="PPTX (+ script) -> DOCX/MD lecture note")
    b.add_argument("pptx")
    b.add_argument("--script", help="TXT/DOCX lecture script")
    b.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    b.add_argument("--out", default="outputs")
    b.add_argument("--title")
    b.add_argument("--backend", choices=["offline", "anthropic"], default="offline")
    b.add_argument("--model")
    a = ap.parse_args(argv)

    backend = OfflineBackend() if a.backend == "offline" else AnthropicBackend(model=a.model)
    report, paths = run_pipeline(a.pptx, a.out, a.template, a.script, backend, a.title)
    for k, v in paths.items():
        print(f"{k:12s} {v}")
    print(f"coverage {report.slide_coverage:.0%}  errors {len(report.errors)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
